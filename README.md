## ComfyUI Jake Upgrade

A [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflow customization by Jake.

## Installation
1. `git clone https://github.com/jakechai/ComfyUI-JakeUpgrade` into the `custom_nodes` folder 
    - e.g. `custom_nodes\ComfyUI-JakeUpgrade`
	
	OR: Install using ComfyUI Manager.
2. Open a Command Prompt/Terminal/etc.
3. Change to the `custom_nodes\ComfyUI-JakeUpgrade` folder you just created 
    - e.g. `cd C:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI-JakeUpgrade`
4.  Install python packages
      - **Windows Standalone installation** (embedded python):
	  
        `../../../python_embeded/python.exe -s -m pip install -r requirements.txt`
	    
		OR: run install.bat.
      - **Manual/non-Windows installation**
        `pip install -r requirements.txt`

## Video Introduction
[Youtube](https://www.youtube.com/watch?v=PKnxhFZNu2c) [Bilibili](https://www.bilibili.com/video/BV1h6421f7AQ/)

## JakeUpgrade Workflow
Main:
- [JK_workflow_tex2img_img2img_SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_tex2img_img2img_SDXL.json)
- [JK_workflow_tex2img_img2img_SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_tex2img_img2img_SD15.json)
- [JK_workflow_img2mesh_CRM&Zero123plus&MVDream&CharacterGen](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_img2mesh_CRM&Zero123plus&MVDream&CharacterGen.json)
- [JK_workflow_img2mesh_Unique3D&Wonder3D&Era3D](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_img2mesh_Unique3D&Wonder3D&Era3D.json)
- [JK_workflow_img2mesh_Zero123&SV3D](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_img2mesh_Zero123&SV3D.json)

(Tips: ComfyUI-3D-Pack needs pytorch 2.3.0+cu121 and xformers, but the latest ComfyUI_windows_portable version uses pytorch 2.3.1+cu121, you should separate those two ComfyUI.)

Other:
- [JK_workflow_Concept](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_Concept.json)
- [JK_workflow_Seamless Texture](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_Seamless%20Texture.json)
- [JK_workflow_Detailer](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_Detailer.json)
- [JK_workflow_Inpaint](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_Inpaint.json)
- [JK_workflow_tex2img_Simple](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_tex2img_Simple.json)
- [JK_workflow_Upscale](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_Upscale.json)
- [JK_Workflow_Mesh-ReMesh_Projection](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_Workflow_Mesh-ReMesh_Projection.json)

## Required Custom Nodes
To use JK_workflow, you need to install:
- [rgthree](https://github.com/rgthree/rgthree-comfy)
- [Comfyroll](https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes)
- [pythongosssss](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)
- [ControlNet AUX](https://github.com/Fannovel16/comfyui_controlnet_aux)
- [Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)
- [Inspire Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack)
- [KJ Nodes](https://github.com/kijai/ComfyUI-KJNodes)
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

Install and copy | replace files (see in replacement folder):
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) : Copy _JK.pack in the replacement folder to `custom_nodes\ComfyUI-Manager\component'.
- [Prompt Stylers](https://github.com/wolfden/ComfyUi_PromptStylers) : Copy new styles (optional).

## JK_workflow : tex2img_img2img_Complete : Introduction
	Hotkey:
		0: usage guide
		\`: overall workflow
		1: base, image selection, & noise injection
		2: embedding, fine tune string, auto prompts, & adv conditioning parameters
		3: lora, controlnet parameters, & adv model parameters
		4: refine parameters
		5: detailer parameters
		6: upscale parameters
		7: In/Out Paint parameters

	Workflow Control:
		All switches in any Workflow panel take effect in realtime.
		All switches in any Select panel also affect sub workflow, but don't take effect in realtime, which needs preprocessing.
		All switches in Parameters panel that affect sub workflow don't take effect in realtime, which needs preprocessing.

	Suggested method:
		Preprocessing needs to be executed before actural generation for switches in Select or Parameters panels to control the sub workflow. 
		Pre-Queue Prompt: It's recommended to disable all processes in the Overall Workflow panel and adjust all sub-workflow-related switches before running Queue Prompt. The state of corresponding switches in Pre-process panels will be changed automatically after the preprocessing.
		Pre-process Pannel: Alternatively, you can preprocess manually by setting the corresponding switches in the Pre-process Pannel to the same state as in the Parameters Pannel, which does not need a Pre-Queue Prompt.

	Metadata:
		All parameters including sub-workflow-related switches will affect the generation result and also the content of Metadata saved with the image.
		In Refine image saving, remove noise_jinection_metadata link if not refining any noise injection process.
		In Upscale image saving, remove noise_jinection_metadata or refine_metadata link if not using Noise Injection or refine process.
		In Detailer image saving, remove noise_jinection_metadata, refine_metadata or upscale_metadata link if not using Noise Injection or refine process.

	SDXL switches:
		Load SDXL Ckpt for Base | Refine | Upscale | Detailer | In/Out Paint
		Load SDXL Vae for Base | Detailer
		FreeU SDXL settings
		Auto Variation SDXL settings
		Disable SD15 ELLA Text Encode (in Base Model Sub Workflow JK🐉)
		Enable SDXL Text Ecode (in Base Model Sub Workflow JK🐉)     (Optional)
		Enable SDXL Refine Text Encode (in Refine Sub Workflow JK🐉) (optional)
		Disable IPAdapter 2 - faceid (in Refine Sub Workflow JK🐉)
		Switch plus and plus-face ipadapter to sdxl_vit-h version
		Switch Image Upscale ControlNet Depth|Tile to sdxl version (in Upscale Sub Workflow JK🐉)
		Switch NNLatentUpscale version to SDXL
		Set Ultimate SD Upscale Tile size to 1024
		Disable SD15 Hand Fix Detailer
		(If it is SD15, choose the opposite)

	Other:
		1. Nodes State JK🐉 uses target nodes' id to control their active | mute | bypass mode. Need to update node_id_list if you make a copy.
		2. The order of Detailer Progress and Upscale Progress can be swapped. Please avoid to form loops. 

## JK_workflow : tex2img_img2img_Complete : Explanation
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/0-1_OverallWorkflow.png)
- Overall Workflow

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/0-2_ImageComparer.png)
- Image Comparer

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-1_ProjectSetting.png)
- Project Setting

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-2_BaseCkptVaeSeed.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-3_BaseModelParameters.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-4_BaseModelSubWorkflowNNoiseInjectionParameter.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/1-5_ImageInputSelect.png)
- Base Model Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/2-1_TI.png)
- TI Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/2-2_FineTuneString.png)
- Fine Tune String Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/2-3_AutoVariationPrompt.png)
- Auto Variation Prompt Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/2-4_AdvancedConditioning.png)
- Advanced Conditioning Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/3-1_Lora.png)
- Lora Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/3-2_ControlNet.png)
- Control Net Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/3-3_AdvancedModel.png)
- Advanced Model Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/4-1_RefineProcessCkptSeed.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/4-2_RefineModelParameters.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/4-3_RefineSubProcessWorkflow.png)
- Refine Process Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-1_UpscaleProcess.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-2_UpscaleCkptSeed.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-3_UpscaleParameters.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-4_UpscaleSubWorkflow.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/5-5_UpscaleNoiseInjection.png)
- Upscale Process Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/6-1_DetailerProcessSelect.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/6-2_DetailerParameters.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/6-3_DetailerSubWorkflow.png)
- Detailer Process Parameters

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/7-1_InOutPaintProcessSelect.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/7-2_InOutPaintCkptVae.png)
![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/7-3_InOutPaintSubWorkflow.png)
- In/Out Paint Process Parameters

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
		Mesh Input Switch JK🐉
		Orbit Pose Input Switch JK🐉
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
	3D Nodes
		Orbit Poses JK🐉
		OrbitLists to OrbitPoses JK🐉
		OrbitPoses to OrbitLists JK🐉

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
- 2024-07-11 - v1.0.6 Noise Injection for Upscale Workflow.
- 2024-07-16 - v1.0.7 Single Image to Mesh Workflow updated.
- 2024-07-21 - v1.0.8 Orbit Poses Constant nodes added. 3 Image to Mesh Workflows updated.

## Workflow Todo List
- ControlNet Preprocess
- IC Light
- Layer Diffuse
- Color Grading
