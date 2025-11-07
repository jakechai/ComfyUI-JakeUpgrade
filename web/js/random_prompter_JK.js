/**
 * JakeUpgrade Prompt Nodes Extension
 * Combined extension for RandomPrompter_JK and RandomPrompterGeek_JK
 */

import { app } from "../../../scripts/app.js";

// 配置常量
const CONFIG = {
    // 原始版本配置
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
    DEFAULT_DESCRIPTION_TEMPLATE: "A masterpiece of work with insane detail and best quality, featuring a masterfully balanced composition and harmonious colors, presenting a groundbreaking concept",
    
    // Geek 版本配置
    GEEK_SELECT_OPTION: "select",
    GEEK_CATEGORY_FORMAT: "[{category_name}]",
    PRIMARY_CATEGORIES: [
        "scene", "motion", "facial_action", "expression", 
        "lighting", "camera", "style", "description"
    ]
};

// 共享工具函数
class PromptUtils {
    static findWidget(node, widgetName) {
        return node.widgets?.find(w => w.name === widgetName);
    }

    static shouldSkipAutoFill(autoFillWidget) {
        return autoFillWidget && autoFillWidget.value === false;
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

    static isUseImageOption(value) {
        return value && value.toLowerCase().startsWith("use image ");
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

    // 添加缺失的方法
    static shouldProcessValue(value) {
        return value && value !== "disable" && value !== "random" && value !== "enable" && 
               !this.isUseImageOption(value);
    }
}

// Geek 版本专用工具函数
class GeekPromptUtils extends PromptUtils {
    static isSelectOption(value) {
        return !value || value === CONFIG.GEEK_SELECT_OPTION;
    }

    static formatCategoryTag(categoryName) {
        return CONFIG.GEEK_CATEGORY_FORMAT.replace("{category_name}", categoryName);
    }

    static addToCustomPrompt(customPromptWidget, tag) {
        if (!customPromptWidget) return;

        let currentValue = customPromptWidget.value || "";
        let newValue = currentValue.trim();
        
        if (newValue && !newValue.endsWith(",") && !newValue.endsWith(" ")) {
            newValue += ", ";
        }
        
        newValue += tag;
        
        customPromptWidget.value = newValue;
    }
}

// 原始版本扩展
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
}

// Geek 版本扩展
class RandomPrompterGeekExtension {
    constructor() {
        this.name = "Comfy.RandomPrompterGeek_JK";
        this.categoryUniquenessCache = new Map();
    }

    async setupAutoFill(node) {
        const autoFillWidget = GeekPromptUtils.findWidget(node, "auto_fill");
        
        // 为每个主要分类设置自动填充
        CONFIG.PRIMARY_CATEGORIES.forEach(category => {
            this.setupCategoryAutoFill(node, category, autoFillWidget);
        });

        // 初始化唯一性缓存
        await this.initializeUniquenessCache(node);
    }

    setupCategoryAutoFill(node, categoryName, autoFillWidget) {
        const categoryWidget = GeekPromptUtils.findWidget(node, categoryName);
        const customPromptWidget = GeekPromptUtils.findWidget(node, "custom_prompt");

        if (!categoryWidget || !customPromptWidget) return;

        // 保存当前实例的引用
        const extensionInstance = this;

        // 参考示例代码的模式：使用 Object.defineProperty 覆盖控件行为
        const originalCallback = categoryWidget.callback;
        
        // 存储实际值的内部属性
        node[`_internal_${categoryName}`] = CONFIG.GEEK_SELECT_OPTION;
        
        // 重写 value 属性 - 修复 this 上下文问题
        Object.defineProperty(categoryWidget, "value", {
            set: function(value) {
                // 存储实际值到内部属性
                node[`_internal_${categoryName}`] = value;
                
                // 如果不是 select 选项，处理自动填充
                if (!GeekPromptUtils.isSelectOption(value) && 
                    !GeekPromptUtils.shouldSkipAutoFill(autoFillWidget)) {
                    
                    // 使用保存的实例引用调用方法
                    extensionInstance.handleCategorySelection(node, categoryName, value, customPromptWidget);
                    
                    // 重置为 select
                    setTimeout(() => {
                        // 直接设置值，避免递归
                        node[`_internal_${categoryName}`] = CONFIG.GEEK_SELECT_OPTION;
                        // 触发UI更新
                        if (categoryWidget.onChange) {
                            categoryWidget.onChange(CONFIG.GEEK_SELECT_OPTION);
                        }
                    }, 100);
                }
                
                // 调用原始回调（如果有）
                if (originalCallback) {
                    originalCallback.call(categoryWidget, value);
                }
            },
            get: function() {
                // 返回内部存储的值
                return node[`_internal_${categoryName}`] || CONFIG.GEEK_SELECT_OPTION;
            }
        });

        // 重写 serializeValue 方法，确保序列化时使用内部值
        categoryWidget.serializeValue = function() {
            return node[`_internal_${categoryName}`] || CONFIG.GEEK_SELECT_OPTION;
        };

        // 初始化内部值
        if (categoryWidget.value !== CONFIG.GEEK_SELECT_OPTION) {
            node[`_internal_${categoryName}`] = categoryWidget.value;
            categoryWidget.value = CONFIG.GEEK_SELECT_OPTION;
        }
    }

    async initializeUniquenessCache(node) {
        // 等待节点完全初始化
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // 收集所有分类名称，检查唯一性
        const allCategories = new Map();
        
        CONFIG.PRIMARY_CATEGORIES.forEach(category => {
            const widget = GeekPromptUtils.findWidget(node, category);
            if (widget && widget.options) {
                // 修复：确保 options 是数组
                let optionsArray = widget.options;
                if (widget.options.values) {
                    // 如果是 ComboWidget 结构，使用 values 数组
                    optionsArray = widget.options.values;
                }
                
                // 确保 optionsArray 是数组且有 forEach 方法
                if (Array.isArray(optionsArray)) {
                    optionsArray.forEach(option => {
                        if (!GeekPromptUtils.isSelectOption(option) && option !== "expression strength") {
                            if (!allCategories.has(option)) {
                                allCategories.set(option, []);
                            }
                            allCategories.get(option).push(category);
                        }
                    });
                }
            }
        });

        // 构建唯一性映射
        this.categoryUniquenessCache.clear();
        for (const [categoryName, sources] of allCategories) {
            this.categoryUniquenessCache.set(categoryName, sources.length > 1);
        }
    }

	handleCategorySelection(node, categoryName, selectedValue, customPromptWidget) {
		// 特殊处理 expression strength
		if (categoryName === "expression" && selectedValue === "expression strength") {
			this.handleExpressionStrength(node, customPromptWidget);
			return;
		}

		// 确定最终的分类标签名称
		let finalCategoryName = selectedValue;
		
		// 检查是否需要添加前缀（如果不唯一）
		if (this.categoryUniquenessCache.get(selectedValue)) {
			// 分类名称不唯一，添加前缀
			// 清理 categoryName（移除数字前缀）
			let cleanCategoryName = categoryName;
			if (cleanCategoryName.includes('-')) {
				cleanCategoryName = cleanCategoryName.split('-').slice(1).join('-');
			}
			finalCategoryName = `${cleanCategoryName}\\${selectedValue}`;
		}

		// 格式化标签
		const tag = GeekPromptUtils.formatCategoryTag(finalCategoryName);
		
		// 添加到 custom_prompt
		GeekPromptUtils.addToCustomPrompt(customPromptWidget, tag);
	}

    handleExpressionStrength(node, customPromptWidget) {
        const expressionStrengthTag = GeekPromptUtils.formatCategoryTag("expression strength");
        GeekPromptUtils.addToCustomPrompt(customPromptWidget, expressionStrengthTag);
    }
}

// 主扩展 - 注册两个节点的扩展
app.registerExtension({
    name: "Comfy.JakeUpgrade.Prompts",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "RandomPrompter_JK") {
            const originalExtension = new RandomPrompterExtension();
            
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
                        originalExtension.parseDescriptionTemplate(node, customDescriptionWidget.value);
                    }
                }, 200);
                
                setTimeout(() => {
                    originalExtension.setupAutoFill(node);
                }, 100);
                
                return ret;
            };
        } 
        else if (nodeData.name === "RandomPrompterGeek_JK") {
            const geekExtension = new RandomPrompterGeekExtension();
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const ret = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                const node = this;
                
                // 为每个节点实例初始化内部状态
                CONFIG.PRIMARY_CATEGORIES.forEach(category => {
                    node[`_internal_${category}`] = CONFIG.GEEK_SELECT_OPTION;
                });
                
                // 延迟设置自动填充，确保所有控件都已初始化
                setTimeout(async () => {
                    await geekExtension.setupAutoFill(node);
                }, 200);
                
                return ret;
            };
        }
    }
});