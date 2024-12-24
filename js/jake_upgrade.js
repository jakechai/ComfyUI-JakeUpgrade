import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";
//import type {LGraphNode} from 'typings/litegraph.js';

//---------------------------------------------------------------------------------------------------------------------//
// Set Node State based on:
//		Impact Pack			https://github.com/ltdrdata/ComfyUI-Impact-Pack
//---------------------------------------------------------------------------------------------------------------------//
function setNodeState(event) {
	let nodes = app.graph._nodes_by_id;
	let node = nodes[event.detail.node_id];
	if(node) {
		if(event.detail.node_mode == 0)
			node.mode = 0;
		else if(event.detail.node_mode == 2)
			node.mode = 2;
		else if(event.detail.node_mode == 4)
			node.mode = 4;
	}
}

api.addEventListener("jakeupgrade-node-state", setNodeState);

//---------------------------------------------------------------------------------------------------------------------//
// Widget Visibility based on:
//		Efficiency Nodes for ComfyUI			https://github.com/jags111/efficiency-nodes-comfyui
//---------------------------------------------------------------------------------------------------------------------//
let origProps = {};

const doesInputWithNameExist = (node, name) => {
    return node.inputs ? node.inputs.some((input) => input.name === name) : false;
};

const HIDDEN_TAG = "tschide";

function toggleWidget(node, widget, show = false, suffix = "") {
    if (!widget || doesInputWithNameExist(node, widget.name)) return;

    // Store the original properties of the widget if not already stored
    if (!origProps[widget.name]) {
        origProps[widget.name] = { origType: widget.type, origComputeSize: widget.computeSize };
    }

    const origSize = node.size;

    // Set the widget type and computeSize based on the show flag
    widget.type = show ? origProps[widget.name].origType : HIDDEN_TAG + suffix;
    widget.computeSize = show ? origProps[widget.name].origComputeSize : () => [0, -4];

    // Recursively handle linked widgets if they exist
    widget.linkedWidgets?.forEach(w => toggleWidget(node, w, ":" + widget.name, show));

    // Calculate the new height for the node based on its computeSize method
    const newHeight = node.computeSize()[1];
    node.setSize([node.size[0], newHeight]);
}
// WIP
function toggleInput(node, widget, AddOrRemove = false, dataType = "") {
    if (!widget) return;
	
	if (AddOrRemove) {
		//if (doesInputWithNameExist(node, widget.name)) return;
		/*
 		node.prototype.addInput = function(widget, dataType) {
			var input = this.inputs[widget];
			if (input) {
				return;
			}

			this.beforeChange();
			this.inputs[widget] = { name: widget, type: dataType };
			this._version++;
			this.afterChange();

			if (this.onInputAdded) {
				this.onInputAdded(widget, dataType);
			}

			if (this.onInputsOutputsChange) {
				this.onInputsOutputsChange();
			}
		}; */
		
		this.addInput(widget, dataType);
	}
    else {
		//if (!doesInputWithNameExist(node, widget.name)) return;
		/*
		node.prototype.removeInput = function(widget) {
			if (!this.inputs[widget]) {
				return false;
			}
			
			delete this.inputs[widget];
			this._version++;
			
			if (this.onInputRemoved) {
				this.onInputRemoved(widget);
			}
			
			if (this.onInputsOutputsChange) {
				this.onInputsOutputsChange();
			}
			return true;
		}; */
		
		this.removeInput(widget);
	}
}

const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

function handleInputModeWidgetsVisibility(node, inputModeValue) {
    // Utility function to generate widget names up to a certain count
    function generateWidgetNames(baseName, count) {
        return Array.from({ length: count }, (_, i) => `${baseName}_${i + 1}`);
    }

    // Common widget groups
	const AnimPromptJKPromptNegWidgets = [...generateWidgetNames("prompt_neg", 20)];
	const LoraStackLoraWidgets = [...generateWidgetNames("lora_weight", 6)];
	const LoraStackModelWidgets = [...generateWidgetNames("model_weight", 6)];
	const LoraStackClipWidgets = [...generateWidgetNames("clip_weight", 6)];
	const TIStackAppendWidgets = [...generateWidgetNames("append", 6)];
	
    const InputModeInvisibilityNodesMap = {
		"Animation Prompt JK": {
			"simple": ["prompt_neg_pre", "prompt_neg_app", ...AnimPromptJKPromptNegWidgets],
			"advanced": []
		},
		"CR Load LoRA JK": {
			"simple": ["model_weight", "clip_weight"],
			"advanced": ["lora_weight"]
		},
		"CR LoRA Stack JK": {
			"simple": [...LoraStackModelWidgets, ...LoraStackClipWidgets],
			"advanced": [...LoraStackLoraWidgets]
		},
		"Embedding Picker Multi JK": {
			"simple": [...TIStackAppendWidgets],
			"advanced": []
		},
	};

    const InputModeWidgetInvisibilityMap = InputModeInvisibilityNodesMap[node.comfyClass];
    
    if (!InputModeWidgetInvisibilityMap || !InputModeWidgetInvisibilityMap[inputModeValue]) return;

    // Reset all widgets to visible
    for (const key in InputModeWidgetInvisibilityMap) {
        for (const widgetName of InputModeWidgetInvisibilityMap[key]) {
            const widget = findWidgetByName(node, widgetName);
            toggleWidget(node, widget, true);
        }
    }

    // Hide the specific widgets for the current input_mode value
    for (const widgetName of InputModeWidgetInvisibilityMap[inputModeValue]) {
        const widget = findWidgetByName(node, widgetName);
        toggleWidget(node, widget, false);
    }
}

function handleWidgetsVisibility(node, countValue, node_type) {
    
    const WidgetInvisibilityNodesMap = {
		"Animation Prompt JK": ["keyframe_frame", "prompt_pos", "prompt_neg"],
		"Animation Value JK": ["keyframe_frame", "keyframe_value"],
		"CR LoRA Stack JK": ["lora", "lora_name", "lora_weight", "model_weight", "clip_weight"],
		"Embedding Picker Multi JK": ["embedding", "embedding_name", "emphasis", "append"],
		"CR Multi-ControlNet Stack JK": ["ControlNet_Unit", "controlnet", "union_type", "controlnet_strength", "start_percent", "end_percent"],
		"CR Multi-ControlNet Param Stack JK": ["ControlNet_Unit", "controlnet_strength", "start_percent", "end_percent"],
	};
	
 	if (node_type === "Animation Prompt JK") {
		
		const inputModeValue = findWidgetByName(node, "input_mode").value;
		const InvisibleWidgetNames = WidgetInvisibilityNodesMap[node_type];
		const promptNegPreWidget = findWidgetByName(node, `prompt_neg_pre`);
		const promptNegPostWidget = findWidgetByName(node, `prompt_neg_app`);
				
		if (inputModeValue === "simple") {
			toggleWidget(node, promptNegPreWidget, false);
			toggleWidget(node, promptNegPostWidget, false);
		}
		else if (inputModeValue === "advanced") {
			toggleWidget(node, promptNegPreWidget, true);
			toggleWidget(node, promptNegPostWidget, true);
		}
		
		for (let i = 1; i <= 20; i++) {
			
			const InvisibleWidget0 = findWidgetByName(node, `${InvisibleWidgetNames[0]}_${i}`);
			const InvisibleWidget1 = findWidgetByName(node, `${InvisibleWidgetNames[1]}_${i}`);
			const InvisibleWidget2 = findWidgetByName(node, `${InvisibleWidgetNames[2]}_${i}`);

			if (i <= countValue) {
				if (inputModeValue === "simple") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, false);
				}
				else if (inputModeValue === "advanced") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, true);
				}
			}
			else {
				toggleWidget(node, InvisibleWidget0, false);
				toggleWidget(node, InvisibleWidget1, false);
				toggleWidget(node, InvisibleWidget2, false);
			}
		}
	}
	else if (node_type === "Animation Value JK") {
		
		for (let i = 1; i <= 20; i++) {
			
			const InvisibleWidgetNames = WidgetInvisibilityNodesMap[node_type];
			const InvisibleWidget0 = findWidgetByName(node, `${InvisibleWidgetNames[0]}_${i}`);
			const InvisibleWidget1 = findWidgetByName(node, `${InvisibleWidgetNames[1]}_${i}`);
			

			if (i <= countValue) {
				toggleWidget(node, InvisibleWidget0, true);
				toggleWidget(node, InvisibleWidget1, true);
			}
			else {
				toggleWidget(node, InvisibleWidget0, false);
				toggleWidget(node, InvisibleWidget1, false);
			}
		}
	}
	else if (node_type === "CR LoRA Stack JK") {
		
		const inputModeValue = findWidgetByName(node, "input_mode").value;
		const InvisibleWidgetNames = WidgetInvisibilityNodesMap[node_type];
		
		for (let i = 1; i <= 6; i++) {
			
			const InvisibleWidget0 = findWidgetByName(node, `${InvisibleWidgetNames[0]}_${i}`);
			const InvisibleWidget1 = findWidgetByName(node, `${InvisibleWidgetNames[1]}_${i}`);
			const InvisibleWidget2 = findWidgetByName(node, `${InvisibleWidgetNames[2]}_${i}`);
			const InvisibleWidget3 = findWidgetByName(node, `${InvisibleWidgetNames[3]}_${i}`);
			const InvisibleWidget4 = findWidgetByName(node, `${InvisibleWidgetNames[4]}_${i}`);

			if (i <= countValue) {
				if (inputModeValue === "simple") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, true);
					toggleWidget(node, InvisibleWidget3, false);
					toggleWidget(node, InvisibleWidget4, false);
				}
				else if (inputModeValue === "advanced") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, false);
					toggleWidget(node, InvisibleWidget3, true);
					toggleWidget(node, InvisibleWidget4, true);
				}
			}
			else {
				toggleWidget(node, InvisibleWidget0, false);
				toggleWidget(node, InvisibleWidget1, false);
				toggleWidget(node, InvisibleWidget2, false);
				toggleWidget(node, InvisibleWidget3, false);
				toggleWidget(node, InvisibleWidget4, false);
			}
		}
	}
	else if (node_type === "Embedding Picker Multi JK") {
		
		const inputModeValue = findWidgetByName(node, "input_mode").value;
		const InvisibleWidgetNames = WidgetInvisibilityNodesMap[node_type];
		
		for (let i = 1; i <= 6; i++) {
			
			const InvisibleWidget0 = findWidgetByName(node, `${InvisibleWidgetNames[0]}_${i}`);
			const InvisibleWidget1 = findWidgetByName(node, `${InvisibleWidgetNames[1]}_${i}`);
			const InvisibleWidget2 = findWidgetByName(node, `${InvisibleWidgetNames[2]}_${i}`);
			const InvisibleWidget3 = findWidgetByName(node, `${InvisibleWidgetNames[3]}_${i}`);

			if (i <= countValue) {
				if (inputModeValue === "simple") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, true);
					toggleWidget(node, InvisibleWidget3, false);
				}
				else if (inputModeValue === "advanced") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, true);
					toggleWidget(node, InvisibleWidget3, true);
				}
			}
			else {
				toggleWidget(node, InvisibleWidget0, false);
				toggleWidget(node, InvisibleWidget1, false);
				toggleWidget(node, InvisibleWidget2, false);
				toggleWidget(node, InvisibleWidget3, false);
			}
		}
	}
	else if (node_type === "CR Multi-ControlNet Stack JK") {
		
		const inputModeValue = findWidgetByName(node, "input_mode").value;
		const InvisibleWidgetNames = WidgetInvisibilityNodesMap[node_type];
		
		for (let i = 0; i <= 5; i++) {
			
			const InvisibleWidget0 = findWidgetByName(node, `${InvisibleWidgetNames[0]}_${i}`);
			const InvisibleWidget1 = findWidgetByName(node, `${InvisibleWidgetNames[1]}_${i}`);
			const InvisibleWidget2 = findWidgetByName(node, `${InvisibleWidgetNames[2]}_${i}`);
			const InvisibleWidget3 = findWidgetByName(node, `${InvisibleWidgetNames[3]}_${i}`);
			const InvisibleWidget4 = findWidgetByName(node, `${InvisibleWidgetNames[4]}_${i}`);
			const InvisibleWidget5 = findWidgetByName(node, `${InvisibleWidgetNames[5]}_${i}`);

			if (i <= countValue) {
				if (inputModeValue === "simple") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, true);
					toggleWidget(node, InvisibleWidget3, true);
					toggleWidget(node, InvisibleWidget4, false);
					toggleWidget(node, InvisibleWidget5, false);
				}
				else if (inputModeValue === "advanced") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, true);
					toggleWidget(node, InvisibleWidget3, true);
					toggleWidget(node, InvisibleWidget4, true);
					toggleWidget(node, InvisibleWidget5, true);
				}
			}
			else {
				toggleWidget(node, InvisibleWidget0, false);
				toggleWidget(node, InvisibleWidget1, false);
				toggleWidget(node, InvisibleWidget2, false);
				toggleWidget(node, InvisibleWidget3, false);
				toggleWidget(node, InvisibleWidget4, false);
				toggleWidget(node, InvisibleWidget5, false);
			}
		}
	}
	else if (node_type === "CR Multi-ControlNet Param Stack JK") {
		
		const inputModeValue = findWidgetByName(node, "input_mode").value;
		const InvisibleWidgetNames = WidgetInvisibilityNodesMap[node_type];
		
		for (let i = 0; i <= 5; i++) {
			
			const InvisibleWidget0 = findWidgetByName(node, `${InvisibleWidgetNames[0]}_${i}`);
			const InvisibleWidget1 = findWidgetByName(node, `${InvisibleWidgetNames[1]}_${i}`);
			const InvisibleWidget2 = findWidgetByName(node, `${InvisibleWidgetNames[2]}_${i}`);
			const InvisibleWidget3 = findWidgetByName(node, `${InvisibleWidgetNames[3]}_${i}`);


			if (i <= countValue) {
				if (inputModeValue === "simple") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, false);
					toggleWidget(node, InvisibleWidget3, false);
				}
				else if (inputModeValue === "advanced") {
					toggleWidget(node, InvisibleWidget0, true);
					toggleWidget(node, InvisibleWidget1, true);
					toggleWidget(node, InvisibleWidget2, true);
					toggleWidget(node, InvisibleWidget3, true);
				}
			}
			else {
				toggleWidget(node, InvisibleWidget0, false);
				toggleWidget(node, InvisibleWidget1, false);
				toggleWidget(node, InvisibleWidget2, false);
				toggleWidget(node, InvisibleWidget3, false);
			}
		}
	}
}
// WIP
function handleInputsAddRemove(node, countValue, node_type) {
	const InputsAddRemoveNodesMap = {
		"CR Multi-ControlNet Stack JK": ["image", "image_MetaData"],
	};
	
 	if (node_type === "CR Multi-ControlNet Stack JK") {
		
		const InputNames = InputsAddRemoveNodesMap[node_type];
		
		for (let i = 1; i <= 5; i++) {
			
			const Input0 = findWidgetByName(node, `${InputNames[0]}_${i}`);
			const Input1 = findWidgetByName(node, `${InputNames[1]}_${i}`);
			
			if (Input0 === null) {
				Input0 = `${InputNames[0]}_${i}`;
			}
			
			if (Input1 === null) {
				Input1 = `${InputNames[1]}_${i}`;
			}
			
			if (i <= countValue) {
				toggleInput(node, Input0, true, "image");
				toggleInput(node, Input1, true, "string");
			}
			else {
				toggleInput(node, Input0, false, "image");
				toggleInput(node, Input1, false, "string");
			}
		}
	}
}

const nodeWidgetHandlers = {
    "Animation Prompt JK": {
        'input_mode': handleAinmPromptJKInputMode,
		'keyframe_count': handleAinmPromptJKFrameCount
    },
	"Animation Value JK": {
		'keyframe_count': handleAinmValueJKFrameCount
    },
	"CR Load LoRA JK": {
		'input_mode': handleLoraJKInputMode,
    },
	"CR LoRA Stack JK": {
		'input_mode': handleLoraStackJKInputMode,
		'lora_count': handleLoraStackJKLoraCount
    },
	"Embedding Picker Multi JK": {
		'input_mode': handleTIStackJKInputMode,
		'embedding_count': handleTIStackJKTICount
    },
	"CR Multi-ControlNet Stack JK": {
		'input_mode': handleCNStackJKInputMode,
		'controlnet_count': handleCNStackJKCNCount
    },
		"CR Multi-ControlNet Param Stack JK": {
		'input_mode': handleCNParamStackJKInputMode,
		'controlnet_count': handleCNParamStackJKCNCount
    },
};

function handleAinmPromptJKInputMode(node, widget) {
    //handleInputModeWidgetsVisibility(node, widget.value);
    handleWidgetsVisibility(node, findWidgetByName(node, "keyframe_count").value, "Animation Prompt JK");
}

function handleAinmPromptJKFrameCount(node, widget) {
    handleWidgetsVisibility(node, widget.value, "Animation Prompt JK");
}

function handleAinmValueJKFrameCount(node, widget) {
    handleWidgetsVisibility(node, widget.value, "Animation Value JK");
}

function handleLoraJKInputMode(node, widget) {
    handleInputModeWidgetsVisibility(node, widget.value);    
}

function handleLoraStackJKInputMode(node, widget) {
    //handleInputModeWidgetsVisibility(node, widget.value);
    handleWidgetsVisibility(node, findWidgetByName(node, "lora_count").value, "CR LoRA Stack JK");
}

function handleLoraStackJKLoraCount(node, widget) {
    handleWidgetsVisibility(node, widget.value, "CR LoRA Stack JK");
}

function handleTIStackJKInputMode(node, widget) {
    //handleInputModeWidgetsVisibility(node, widget.value);
    handleWidgetsVisibility(node, findWidgetByName(node, "embedding_count").value, "Embedding Picker Multi JK");
}

function handleTIStackJKTICount(node, widget) {
    handleWidgetsVisibility(node, widget.value, "Embedding Picker Multi JK");
}

function handleTIStackJKCount(node, widget) {
    handleWidgetsVisibility(node, widget.value, "Embedding Picker Multi JK");
}

function handleCNStackJKInputMode(node, widget) {
    //handleInputModeWidgetsVisibility(node, widget.value);
    handleWidgetsVisibility(node, findWidgetByName(node, "controlnet_count").value - 1, "CR Multi-ControlNet Stack JK");
}

function handleCNStackJKCNCount(node, widget) {
    handleWidgetsVisibility(node, widget.value - 1, "CR Multi-ControlNet Stack JK");
	//WIP
	//handleInputsAddRemove(node, widget.value - 1, "CR Multi-ControlNet Stack JK");
}

function handleCNParamStackJKInputMode(node, widget) {

    handleWidgetsVisibility(node, findWidgetByName(node, "controlnet_count").value - 1, "CR Multi-ControlNet Param Stack JK");
}

function handleCNParamStackJKCNCount(node, widget) {
    handleWidgetsVisibility(node, widget.value - 1, "CR Multi-ControlNet Param Stack JK");
}

function widgetLogic(node, widget) {
    // Retrieve the handler for the current node title and widget name
    const handler = nodeWidgetHandlers[node.comfyClass]?.[widget.name];
    if (handler) {
        handler(node, widget);
    }
}

app.registerExtension({
    name: "Comfy.JakeUpgrade",
	
    nodeCreated(node) {
        for (const w of node.widgets || []) {
            let widgetValue = w.value;

            // Store the original descriptor if it exists
            let originalDescriptor = Object.getOwnPropertyDescriptor(w, 'value');

            widgetLogic(node, w);
			
            Object.defineProperty(w, 'value', {
                get() {
                    // If there's an original getter, use it. Otherwise, return widgetValue.
                    let valueToReturn = originalDescriptor && originalDescriptor.get
                        ? originalDescriptor.get.call(w)
                        : widgetValue;

                    return valueToReturn;
                },
                set(newVal) {

                    // If there's an original setter, use it. Otherwise, set widgetValue.
                    if (originalDescriptor && originalDescriptor.set) {
                        originalDescriptor.set.call(w, newVal);
                    } else {
                        widgetValue = newVal;
                    }

                    widgetLogic(node, w);
                }
            });
        }
        setTimeout(() => {initialized = true;}, 500);
    }
});