/**
 * RandomPrompter_JK Auto-fill Extension
 * Auto-fills custom fields when menu selections change
 * Handles expression and exp_str combination for custom_expression
 * Handles description template for custom_description
 * Supports multi-level directory structure for style/vision
 */

import { app } from "../../../scripts/app.js";

// 配置常量
const CONFIG = {
    IMAGE_TYPE_MAPPING: {
        "scene": "scene",
        "motion": "character pose", 
        "facial_action": "character face action",
        "expression": "character face expression",
        "lighting": "lighting",
        "camera": "view angle",
        "style": "style"
    },
    DEFAULT_EXP_STR: "quite",
    DEFAULT_DESCRIPTION_TEMPLATE: "A masterpiece of work with insane detail and best quality, featuring a masterfully balanced composition and harmonious colors, presenting a groundbreaking concept"
};

// 公共工具函数
class PromptUtils {
    static findWidget(node, widgetName) {
        return node.widgets?.find(w => w.name === widgetName);
    }

    static shouldSkipAutoFill(autoFillWidget) {
        return autoFillWidget && autoFillWidget.value === false;
    }

    static isUseImageOption(value) {
        return value && value.toLowerCase().startsWith("use image ");
    }

    static shouldProcessValue(value) {
        return value && value !== "disable" && value !== "random" && value !== "enable";
    }

    static removeCategoryPrefix(value) {
        if (!value || value === "enable" || value === "disable" || value === "random") {
            return value;
        }
        
        const lastBackslashIndex = value.lastIndexOf('\\');
        if (lastBackslashIndex !== -1) {
            return value.substring(lastBackslashIndex + 1);
        }
        return value;
    }

    static smartProcessValue(value) {
        if (!value || value === "enable" || value === "disable" || value === "random") {
            return value;
        }
        
        return this.removeCategoryPrefix(value);
    }

    static getImageRefString(choice, category) {
        const match = choice.toLowerCase().match(/use image (\d+)/);
        if (match) {
            const imageNum = match[1];
            const imageType = CONFIG.IMAGE_TYPE_MAPPING[category] || category;
            return `use image ${imageNum} ${imageType}`;
        }
        return null;
    }
}

// 扩展功能实现类
class RandomPrompterExtension {
    constructor() {
        this.name = "Comfy.RandomPrompter_JK";
    }

    setupAutoFill(node) {
        const autoFillWidget = PromptUtils.findWidget(node, "auto_fill");
        
        // 定义字段映射
        const fieldMappings = [
            { source: "scene", target: "custom_scene" },
            { source: "motion", target: "custom_motion" },
            { source: "camera", target: "custom_camera" },
            { source: "style", target: "custom_style" },
            { source: "lighting", target: "custom_lighting" },
            { source: "description", target: "custom_description" }
        ];

        // 为每个字段映射设置自动填充
        fieldMappings.forEach(mapping => {
            this.setupFieldAutoFill(node, mapping.source, mapping.target, autoFillWidget);
        });

        // 单独处理特殊字段
        this.setupFacialActionAutoFill(node, autoFillWidget);
        this.setupExpressionAutoFill(node, autoFillWidget);
    }

    setupFieldAutoFill(node, sourceField, targetField, autoFillWidget) {
        const sourceWidget = PromptUtils.findWidget(node, sourceField);
        const targetWidget = PromptUtils.findWidget(node, targetField);

        if (!sourceWidget || !targetWidget) return;

        const originalCallback = sourceWidget.callback;
        sourceWidget.callback = (value) => {
            if (originalCallback) {
                originalCallback.call(sourceWidget, value);
            }

            if (PromptUtils.shouldSkipAutoFill(autoFillWidget)) {
                return;
            }

            // 检查是否为"use image"选项
            if (PromptUtils.isUseImageOption(value)) {
                const imageRef = PromptUtils.getImageRefString(value, sourceField);
                if (imageRef) {
                    this.autoFillCustomField(node, targetField, imageRef);
                }
            }
            // 自动填充逻辑
            else if (PromptUtils.shouldProcessValue(value)) {
                const cleanValue = PromptUtils.smartProcessValue(value);
                
                if (sourceField === "description") {
                    this.updateDescriptionCustomField(node, value, cleanValue);
                } else {
                    this.autoFillCustomField(node, targetField, cleanValue);
                }
            }
            
            node.setDirtyCanvas(true, true);
        };
    }

    setupFacialActionAutoFill(node, autoFillWidget) {
        const facialActionWidget = PromptUtils.findWidget(node, "facial_action");
        const customFacialActionWidget = PromptUtils.findWidget(node, "custom_facial_action");

        if (!facialActionWidget || !customFacialActionWidget) return;

        const originalCallback = facialActionWidget.callback;
        facialActionWidget.callback = (value) => {
            if (originalCallback) {
                originalCallback.call(facialActionWidget, value);
            }
            
            if (PromptUtils.shouldSkipAutoFill(autoFillWidget)) {
                return;
            }
            
            if (PromptUtils.isUseImageOption(value)) {
                const imageRef = PromptUtils.getImageRefString(value, "facial_action");
                if (imageRef) {
                    this.autoFillCustomField(node, "custom_facial_action", imageRef);
                }
            }
            else if (PromptUtils.shouldProcessValue(value)) {
                const cleanValue = PromptUtils.smartProcessValue(value);
                this.autoFillCustomField(node, "custom_facial_action", cleanValue);
            }
            
            node.setDirtyCanvas(true, true);
        };
    }

    setupExpressionAutoFill(node, autoFillWidget) {
        const expressionWidget = PromptUtils.findWidget(node, "expression");
        const customExpressionWidget = PromptUtils.findWidget(node, "custom_expression");

        if (!expressionWidget || !customExpressionWidget) return;

        const originalCallback = expressionWidget.callback;
        expressionWidget.callback = (value) => {
            if (originalCallback) {
                originalCallback.call(expressionWidget, value);
            }
            
            if (PromptUtils.shouldSkipAutoFill(autoFillWidget)) {
                return;
            }
            
            if (PromptUtils.isUseImageOption(value)) {
                const imageRef = PromptUtils.getImageRefString(value, "expression");
                if (imageRef) {
                    this.autoFillCustomField(node, "custom_expression", imageRef);
                }
            }
            else if (PromptUtils.shouldProcessValue(value)) {
                const combination = this.getExpressionCombination(node);
                if (combination) {
                    this.autoFillCustomField(node, "custom_expression", combination);
                }
            }
            
            node.setDirtyCanvas(true, true);
        };
    }

    getExpressionCombination(node) {
        const expStrWidget = PromptUtils.findWidget(node, "exp_str");
        const expressionWidget = PromptUtils.findWidget(node, "expression");
        
        let expStrValue = "";
        let expressionValue = "";

        if (expStrWidget && expStrWidget.value) {
            expStrValue = PromptUtils.smartProcessValue(expStrWidget.value);
        }

        if (expressionWidget && expressionWidget.value && 
            PromptUtils.shouldProcessValue(expressionWidget.value)) {
            expressionValue = PromptUtils.smartProcessValue(expressionWidget.value);
        }

        let combination = "";
        if (expStrValue && expressionValue) {
            combination = `${expStrValue} ${expressionValue}`;
        } else if (expressionValue) {
            combination = expressionValue;
        }
        
        return combination;
    }

    autoFillCustomField(node, customFieldName, value) {
        const customWidget = PromptUtils.findWidget(node, customFieldName);
        if (!customWidget) return;

        let newValue = value;
        if (customWidget.value && customWidget.value.trim() !== "") {
            const existingValue = customWidget.value.trim();
            const cleanExisting = existingValue.replace(/,\s*$/, "");
            newValue = cleanExisting + ", " + value;
        }

        if (!newValue.endsWith(",")) {
            newValue += ",";
        }

        customWidget.value = newValue;
    }

    updateDescriptionCustomField(node, fullValue, cleanValue) {
        const customDescriptionWidget = PromptUtils.findWidget(node, "custom_description");
        if (!customDescriptionWidget) return;

        const categoryMatch = fullValue.match(/^([^\\]+)\\/);
        if (!categoryMatch) {
            return;
        }

        const category = categoryMatch[1];
        
        if (node.descriptionSelections.hasOwnProperty(category)) {
            node.descriptionSelections[category] = cleanValue;
        }

        const descriptionTemplate = this.buildDescriptionTemplate(node);
        customDescriptionWidget.value = descriptionTemplate;
    }

    buildDescriptionTemplate(node) {
        const { sensory, detail, quality, composition, color, creativity } = node.descriptionSelections;
        
        const sensoryText = sensory || "masterpiece";
        const detailText = detail || "insane detail";
        const qualityText = quality || "best quality";
        const compositionText = composition || "masterfully balanced composition";
        const colorText = color || "harmonious colors";
        const creativityText = creativity || "groundbreaking concept";
        
        return `A ${sensoryText} of work with ${detailText} and ${qualityText}, featuring a ${compositionText} and ${colorText}, presenting a ${creativityText}`;
    }

    parseDescriptionTemplate(node, descriptionText) {
        if (!descriptionText) return;
        
        if (descriptionText === CONFIG.DEFAULT_DESCRIPTION_TEMPLATE) {
            node.descriptionSelections.sensory = "";
            node.descriptionSelections.detail = "";
            node.descriptionSelections.quality = "";
            node.descriptionSelections.composition = "";
            node.descriptionSelections.color = "";
            node.descriptionSelections.creativity = "";
            return;
        }
        
        try {
            const regex = /^A\s+([^,]+?)\s+with\s+([^,]+?)\s+and\s+([^,]+?),\s+featuring\s+a\s+([^,]+?)\s+and\s+([^,]+?),\s+presenting\s+a\s+([^,.]+?)$/;
            const match = descriptionText.match(regex);
            
            if (match && match.length === 7) {
                node.descriptionSelections.sensory = match[1].trim();
                node.descriptionSelections.detail = match[2].trim();
                node.descriptionSelections.quality = match[3].trim();
                node.descriptionSelections.composition = match[4].trim();
                node.descriptionSelections.color = match[5].trim();
                node.descriptionSelections.creativity = match[6].trim();
                return;
            }
            
            // 分步骤解析
            const sensoryMatch = descriptionText.match(/^A\s+([^,]+?)(?=\s+with)/);
            if (sensoryMatch) {
                node.descriptionSelections.sensory = sensoryMatch[1].trim();
            }
            
            const detailMatch = descriptionText.match(/with\s+([^,]+?)(?=\s+and)/);
            if (detailMatch) {
                node.descriptionSelections.detail = detailMatch[1].trim();
            }
            
            const qualityMatch = descriptionText.match(/and\s+([^,]+?)(?=,\s+featuring)/);
            if (qualityMatch) {
                node.descriptionSelections.quality = qualityMatch[1].trim();
            }
            
            const compositionMatch = descriptionText.match(/featuring\s+a\s+([^,]+?)(?=\s+and)/);
            if (compositionMatch) {
                node.descriptionSelections.composition = compositionMatch[1].trim();
            }
            
            const colorMatch = descriptionText.match(/and\s+([^,]+?)(?=,\s+presenting)/);
            if (colorMatch) {
                const featuringIndex = descriptionText.indexOf("featuring");
                const andIndex = descriptionText.indexOf("and", featuringIndex);
                if (andIndex !== -1) {
                    node.descriptionSelections.color = colorMatch[1].trim();
                }
            }
            
            const creativityMatch = descriptionText.match(/presenting\s+a\s+([^,.]+)/);
            if (creativityMatch) {
                node.descriptionSelections.creativity = creativityMatch[1].trim();
            }
            
        } catch (error) {
            console.error("RandomPrompter_JK: 解析描述模板时出错:", error);
            node.descriptionSelections.sensory = "";
            node.descriptionSelections.detail = "";
            node.descriptionSelections.quality = "";
            node.descriptionSelections.composition = "";
            node.descriptionSelections.color = "";
            node.descriptionSelections.creativity = "";
        }
    }

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "RandomPrompter_JK") {
            return;
        }

        const extensionInstance = this;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const ret = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            const node = this;
            
            // 为每个节点实例添加状态存储
            node.currentExpStr = CONFIG.DEFAULT_EXP_STR;
            
            // 为每个节点实例添加description选择状态存储
            node.descriptionSelections = {
                sensory: "",
                detail: "",
                quality: "",
                composition: "",
                color: "",
                creativity: ""
            };
            
            // 在控件初始化后解析现有内容
            setTimeout(() => {
                const customDescriptionWidget = PromptUtils.findWidget(node, "custom_description");
                if (customDescriptionWidget && customDescriptionWidget.value) {
                    extensionInstance.parseDescriptionTemplate(node, customDescriptionWidget.value);
                }
            }, 200);
            
            setTimeout(() => {
                extensionInstance.setupAutoFill(node);
            }, 100);
            
            return ret;
        };
    }
}

// 创建扩展实例并注册
const extension = new RandomPrompterExtension();
app.registerExtension(extension);
