## ComfyUI Jake Upgrade

A [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflow customization by Jake.

## Installation
1. `git clone https://github.com/jakechai/ComfyUI-JakeUpgrade` into the `custom_nodes` folder 
    - e.g. `custom_nodes\ComfyUI-JakeUpgrade`
	OR:
	Install using ComfyUI Manager.
2. Open a Command Prompt/Terminal/etc.
3. Change to the `custom_nodes\ComfyUI-JakeUpgrade` folder you just created 
    - e.g. `cd C:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI-JakeUpgrade`
4.  Install python packages
      - **Windows Standalone installation** (embedded python):
	   run install.bat
	   OR:
       `../../../python_embeded/python.exe -s -m pip install -r requirements.txt`
      - **Manual/non-Windows installation**   
        `pip install -r requirements.txt`

## Video Introduction
Youtube
Bilibili

## JakeUpgrade Workflow
Main:
- [JK_workflow_tex2img_img2img_Complete](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_tex2img_img2img_Complete.json)
- [JK_workflow_Seamless Texture](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_Seamless%20Texture.json)
- [JK_workflow_img2mesh_single](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_img2mesh_single.json)
- [JK_workflow_img2mesh_multi](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_img2mesh_multi.json)

Other:
- [JK_workflow_Concept](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/JK_workflow_Concept.json)
- [JK_workflow_Detailer](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/JK_workflow_Detailer.json)
- [JK_workflow_Inpaint](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/JK_workflow_Inpaint.json)
- [JK_workflow_tex2img_Simple](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/JK_workflow_tex2img_Simple.json)
- [JK_workflow_Upscale](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/JK_workflow_Upscale.json)

## Required Custom Nodes
To use JK_workflow, you need to install:
- [rgthree](https://github.com/rgthree/rgthree-comfy)
- [Comfyroll](https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes)
- [pythongosssss](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)
- [ControlNet AUX](https://github.com/Fannovel16/comfyui_controlnet_aux)
- [Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)
- [Inspire Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack)
- [WD14 Tagger](https://github.com/pythongosssss/ComfyUI-WD14-Tagger)
- [ComfyUI Noise](https://github.com/BlenderNeko/ComfyUI_Noise)
- [IP Adapter Plus](https://github.com/cubiq/ComfyUI_IPAdapter_plus)
- [Face Analysis](https://github.com/cubiq/ComfyUI_FaceAnalysis)
- [StyleAligned](https://github.com/brianfitzgerald/style_aligned_comfy)
- [NNLatentUpscale](https://github.com/Ttl/ComfyUi_NNLatentUpscale)
- [Dynamic Prompts](https://github.com/adieyal/comfyui-dynamicprompts)
- [One Button Prompt](https://github.com/AIrjen/OneButtonPrompt)
- [ComfyUI ELLA](https://github.com/TencentQQGYLab/ComfyUI-ELLA)
- [Essentials](https://github.com/cubiq/ComfyUI_essentials)
- [WAS Node Suite](https://github.com/WASasquatch/was-node-suite-comfyui)
- [Ultimate SD Upscale](https://github.com/ssitu/ComfyUI_UltimateSDUpscale)
- [ComfyUI 3D Pack](https://github.com/MrForExample/ComfyUI-3D-Pack)
- [Seamless tiling](https://github.com/spinagon/ComfyUI-seamless-tiling)
- [Portrait Master](https://github.com/florestefano1975/comfyui-portrait-master)
- [JakeUpgrade](https://github.com/jakechai/ComfyUI-JakeUpgrade)

Install and copy | replace files (optional, see in replacement folder):
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) : Copy _JK.pack in the replacement folder to `custom_nodes\ComfyUI-Manager\component'.
- [Prompt Stylers](https://github.com/wolfden/ComfyUi_PromptStylers) : Copy new styles.
- [Segment Anything](https://github.com/storyicon/comfyui_segment_anything) : Replace \_\_init\_\_.py to disable requirements installation.

## JakeUpgrade Custom Nodes
	Misc Nodes
		SD1.5 Aspect Ratio JK🐉
		SDXL Aspect Ratio JK🐉
    Reroute Nodes
		Reroute List JK🐉
		Reroute Ckpt JK🐉
		Reroute Vae JK🐉
		Reroute Sampler JK🐉
		Reroute Upscale JK🐉
		Reroute Resize JK🐉
    ControlNet Nodes
		Apply ControlNet JK🐉
		Multi-ControlNet Stack JK🐉
		Apply Multi-ControlNet JK🐉
    LoRA Nodes
		Load LoRA JK🐉
		LoRA Stack JK🐉
    Embedding Nodes
		Embedding Picker JK🐉
		Embedding Picker Multi JK🐉
    Loader Nodes
		Ckpt Loader JK🐉
		Vae Loader JK🐉
		Sampler Loader JK🐉
		Upscale Model Loader JK🐉
    Pipe Nodes
		Nodes State JK🐉
		Ksampler Parameters JK🐉
		Project Setting JK🐉
		Base Model Parameters JK🐉
		Base Model Parameters Extract JK🐉
		Base Image Parameters Extract JK🐉
		Base Model Pipe JK🐉
		Base Model Pipe Extract JK🐉
		Refine Pipe JK🐉
		Refine Pipe Extract JK🐉
		Noise Injection Parameters JK🐉
		Refine Model Parameters JK🐉
		Refine 1 Parameters Extract JK🐉
		Refine 2 Parameters Extract JK🐉
		Upscale Model Parameters JK🐉
		Image Upscale Parameters Extract JK🐉
		Latent Upscale Parameters Extract JK🐉
		Upscale Model Parameters Extract JK🐉
		Detailer Parameters JK🐉
		Pipe End JK🐉
		Metadata Pipe JK🐉
		Metadata Pipe Extract JK🐉
    Image Nodes
		Save Image With Metadata JK🐉
		Save Image With Metadata Flow JK🐉
		Load Image With Metadata JK🐉
		Enchance And Resize Hint Images JK🐉
    Animation Nodes
		Animation Prompt JK🐉
		Animation Value JK🐉
    Logic switches Nodes
		Boolean JK🐉
		Image Input Switch JK🐉
		Mask Input Switch JK🐉
		Int Input Switch JK🐉
		Float Input Switch JK🐉
		Latent Input Switch JK🐉
		Conditioning Input Switch JK🐉
		Clip Input Switch JK🐉
		Model Input Switch JK🐉
		ControlNet Input Switch JK🐉
		Text Input Switch JK🐉
		VAE Input Switch JK🐉
		Switch Model and CLIP JK🐉
		Pipe Input Switch JK🐉
		Impact Pipe Input Switch JK🐉
    ComfyMath Fix Nodes
		BoolToInt JK🐉
		IntToBool JK🐉
		BoolUnaryOp JK🐉
		BoolBinaryOp JK🐉
		FloatUnaryCon JK🐉
		FloatBinaryCon JK🐉
		IntUnaryCon JK🐉
		IntBinaryCon JK🐉
		NumberUnaryCon JK🐉
		NumberBinaryCon JK🐉
		Vec2UnaryCon JK🐉
		Vec2BinaryCon JK🐉
		Vec2ToFloatUnaryOp JK🐉
		Vec2ToFloatBinaryOp JK🐉
		Vec2FloatOp JK🐉
		Vec3UnaryCon JK🐉
		Vec3BinaryCon JK🐉
		Vec3ToFloatUnaryOp JK🐉
		Vec3ToFloatBinaryOp JK🐉
		Vec3FloatOp JK🐉
		Vec4UnaryCon JK🐉
		Vec4BinaryCon JK🐉
		Vec4ToFloatUnaryOp JK🐉
		Vec4ToFloatBinaryOp JK🐉
		Vec4FloatOp JK🐉
    ComfyMath Nodes
		FloatToInt JK🐉
		IntToFloat JK🐉
		IntToNumber JK🐉
		NumberToInt JK🐉
		FloatToNumber JK🐉
		NumberToFloat JK🐉
		ComposeVec2 JK🐉
		ComposeVec3 JK🐉
		ComposeVec4 JK🐉
		BreakoutVec2 JK🐉
		BreakoutVec3 JK🐉
		BreakoutVec4 JK🐉
		FloatUnaryOp JK🐉
		FloatBinaryOp JK🐉
		IntUnaryOp JK🐉
		IntBinaryOp JK🐉
		NumberUnaryOp JK🐉
		NumberBinaryOp JK🐉
		Vec2UnaryOp JK🐉
		Vec2BinaryOp JK🐉
		Vec3UnaryOp JK🐉
		Vec3BinaryOp JK🐉
		Vec4UnaryOp JK🐉
		Vec4BinaryOp JK🐉
    Simple Evaluate Nodes
		Evaluate Ints JK🐉
		Evaluate Floats JK🐉
		Evaluate String JK🐉
    	Evaluate Examples JK🐉

## JakeUpgrade Group Nodes
	Tools
		JK🐉::CLIPSegMask
		JK🐉::Pad Image for Outpainting
		JK🐉::SegAnythingMask
	Workflow
		JK🐉::Concept
		JK🐉::Inpaint Simple
		JK🐉::Inpaint Checkpoint
		JK🐉::Outpaint Checkpoint
		JK🐉::Tex2Img

## Reference Custom Nodes
Jake Upgrade Nodes are inspired by:
- [rgthree](https://github.com/rgthree/rgthree-comfy)
- [Comfyroll](https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes)
- [Efficiency Nodes](https://github.com/jags111/efficiency-nodes-comfyui)
- [ControlNet AUX](https://github.com/Fannovel16/comfyui_controlnet_aux)
- [Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)
- [Image Saver](https://github.com/giriss/comfy-image-saver)
- [Prompt Reader](https://github.com/receyuki/comfyui-prompt-reader-node)
- [ComfyMath](https://github.com/evanspearman/ComfyMath)
- [Embedding Picker](https://github.com/Tropfchen/ComfyUI-Embedding_Picker)

## Changelog
- 2024-06-23 - v1.0.0 released.
