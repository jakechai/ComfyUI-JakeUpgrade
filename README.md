## ComfyUI Jake Upgrade

A [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflow customization by Jake.

If you like what I share, please support me with [PayPal](https://paypal.me/jakechaikefu).

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
- txt2img&img2img workflow: [Youtube](https://www.youtube.com/watch?v=PKnxhFZNu2c) [Bilibili](https://www.bilibili.com/video/BV1h6421f7AQ/)
- txt2img&img2img SD3 workflow: [Youtube](https://youtu.be/MZBNzaWHdr8) [Bilibili](https://www.bilibili.com/video/BV1ceHheqEru/)
- txt2img&img2img SAI API workflow: [Youtube](https://www.youtube.com/watch?v=4DWWUQij9jM) [Bilibili](https://www.bilibili.com/video/BV1QR1BYUE5r/)
- prompt generation workflow: [Youtube](https://youtu.be/h_2PimL3iXY) [Bilibili](https://www.bilibili.com/video/BV1FZp4ebEjK/)
- inpaint workflow: [Youtube](https://www.youtube.com/watch?v=A9nABNizMdY) [Bilibili](https://www.bilibili.com/video/BV1wd4ge8EQf/)
- img2mesh workflow: [Youtube](https://www.youtube.com/watch?v=CbG2Vq3kps0) [Bilibili](https://www.bilibili.com/video/BV1CE4m1R7br/)
- 3D-Pack Installation Tips： [Youtube](https://www.youtube.com/watch?v=RjuoLMCpvbI) [Bilibili](https://www.bilibili.com/video/BV1Nm421375F/)
- 3D-Pack Algorithm Comparison： [Youtube](https://www.youtube.com/watch?v=E7Oj8UUGLic) [Bilibili](https://www.bilibili.com/video/BV1CU411U7y4/)

## JakeUpgrade Workflow

### Main

- [JK_workflow_txt2img_img2img_SD15](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_txt2img_img2img_SD15.json)
- [JK_workflow_txt2img_img2img_SDXL](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_txt2img_img2img_SDXL.json)
- [JK_workflow_txt2img_img2img_SD3](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_txt2img_img2img_SD3.json)
- [JK_workflow_txt2img_img2img_Flux](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_txt2img_img2img_Flux.json)
- [JK_workflow_txt2img_img2img_SAIAPI](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_txt2img_img2img_SAIAPI.json)
- [JK_workflow_txt2prompt_img2prompt](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_txt2prompt_img2prompt.json)
- [JK_workflow_img2mesh_CRM&Zero123plus&MVDream&CharacterGen](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_img2mesh_CRM&Zero123plus&MVDream&CharacterGen.json)
- [JK_workflow_img2mesh_Unique3D&Wonder3D&Era3D](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_img2mesh_Unique3D&Wonder3D&Era3D.json)
- [JK_workflow_img2mesh_Zero123&SV3D](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_img2mesh_Zero123&SV3D.json)
- [JK_workflow_img2mesh_3DGS](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Main/JK_workflow_img2mesh_3DGS.json)

> [!NOTE]
> - ComfyUI-3D-Pack needs pytorch 2.4.0+cu121 and xformers, but the latest ComfyUI_windows_portable version uses pytorch 2.4.1+cu124 (or higher), you should separate those two ComfyUI.  
> - ComfyUI-3D-Pack 3DMesh | 3DGS Preview not working seems to be related to the frontend change of ComfyUI. Fall back to the legacy frontend by adding `--front-end-version Comfy-Org/ComfyUI_legacy_frontend@latest` to the command line argument. [ComfyUI/pull/4379](https://github.com/comfyanonymous/ComfyUI/pull/4379).  
> - [CXH joy caption](https://github.com/StartHua/Comfyui_CXH_joy_caption) conflicts with [VLM Nodes](https://github.com/gokayfem/ComfyUI_VLM_nodes) and is not included in the prompt generation workflow.

### Module

- [JK_workflow_Refine](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_04_Refine.json)
- [JK_workflow_Upscale 1st](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_05_Upscale_1st.json)
- [JK_workflow_Upscale 2nd](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_05_Upscale_2nd.json)
- [JK_workflow_Detailer](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_06_Detailer.json)
- [JK_workflow_HandFix](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_06_Detailer_HandFix.json)
- [JK_workflow_Inpaint](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_07_Inpaint.json)
- [JK_workflow_NoiseInjectionVariation](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_Workflow_NoiseInjectionVariation.json)
- [JK_workflow_Concept](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_Concept.json)
- [JK_workflow_Seamless Texture](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_Seamless%20Texture.json)
- [JK_workflow_txt2img_Simple](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_txt2img_Simple.json)
- [JK_workflow_Flux_KSampler](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_workflow_FluxKSampler.json)
- [JK_Workflow_Mesh-ReMesh_Projection](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/Workflow/Module/JK_Workflow_Mesh-ReMesh_Projection.json)

## Required Custom Nodes

### Common

- [rgthree](https://github.com/rgthree/rgthree-comfy)
- [pythongosssss](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)
- [ControlNet AUX](https://github.com/Fannovel16/comfyui_controlnet_aux)
- [Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)
- [IP Adapter Plus](https://github.com/cubiq/ComfyUI_IPAdapter_plus)
- [KJ Nodes](https://github.com/kijai/ComfyUI-KJNodes)
- [Essentials](https://github.com/cubiq/ComfyUI_essentials)
- [JakeUpgrade](https://github.com/jakechai/ComfyUI-JakeUpgrade)

### txt2img_img2img workflow

- [Inspire Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack)
- [WAS Node Suite](https://github.com/WASasquatch/was-node-suite-comfyui)
- [Comfyroll](https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes)
- [Layer Style](https://github.com/chflame163/ComfyUI_LayerStyle)
- [Segment Anything](https://github.com/storyicon/comfyui_segment_anything)
- [NNLatentUpscale](https://github.com/Ttl/ComfyUi_NNLatentUpscale)
- [Ultimate SD Upscale](https://github.com/ssitu/ComfyUI_UltimateSDUpscale)
- [Seamless tiling](https://github.com/spinagon/ComfyUI-seamless-tiling)
- [ComfyUI Noise](https://github.com/BlenderNeko/ComfyUI_Noise)
- [Face Analysis](https://github.com/cubiq/ComfyUI_FaceAnalysis)
- [StyleAligned](https://github.com/brianfitzgerald/style_aligned_comfy)
- [ComfyUI ELLA](https://github.com/TencentQQGYLab/ComfyUI-ELLA)
- [Dynamic Prompts](https://github.com/adieyal/comfyui-dynamicprompts)
- [One Button Prompt](https://github.com/AIrjen/OneButtonPrompt)
- [Portrait Master](https://github.com/florestefano1975/comfyui-portrait-master)
- [Flux Prompt Generator](https://github.com/fairy-root/Flux-Prompt-Generator)
- [Merlin Magic Photo Prompter](https://github.com/Xclbr7/ComfyUI-Merlin)
- [WD14 Tagger](https://github.com/pythongosssss/ComfyUI-WD14-Tagger)
- [VLM Nodes](https://github.com/gokayfem/ComfyUI_VLM_nodes)
- [IF AI Tools](https://github.com/if-ai/ComfyUI-IF_AI_tools)
- [ComfyUI SAI API](https://github.com/Stability-AI/ComfyUI-SAI_API)
- [comfyUI Fal API](https://github.com/gokayfem/ComfyUI-fal-API)

### img2mesh workflow

- [ComfyUI 3D Pack](https://github.com/MrForExample/ComfyUI-3D-Pack)

### Install and copy | replace files (optional)

- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) : Copy `_JK.pack` in the replacement folder to `custom_nodes\ComfyUI-Manager\component`.
- [Prompt Stylers](https://github.com/wolfden/ComfyUi_PromptStylers) : Copy new styles.
- [ComfyUI SAI API](https://github.com/Stability-AI/ComfyUI-SAI_API) : (Workaround before ComfyUI SAI API approves my pull request)Copy and replace files in `custom_nodes\ComfyUI-SAI_API`

> [!NOTE]
> - Group Nodes are saved and can only used in the current workflow. Copy `_JK.pack` and set `Component: Use my version` in the ComfyUI Manager Menu if you want all the latest Jake Upgrade group nodes available for other workflows.

## JK_workflow : txt2img_img2img
<details>
<summary><b>Introduction</b></summary>

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
		Image Resolution | AIO resolution
		Load SDXL Ckpt | Vae for Base | Refine | Upscale | Detailer | In/Out Paint
		FreeU SDXL settings
		Auto Variation SDXL settings
		Disable SD15 ELLA Text Encode (in Base Model Sub Workflow JK🐉)
		Enable SDXL Text Ecode (in Base Model Sub Workflow JK🐉) (Optional)
		Enable SDXL Dual Clip (in Base Model Sub Workflow JK🐉) (Optional)
		Enable SDXL Refine Text Encode (in Refine Sub Workflow JK🐉) (optional)
		Switch plus, plus-face, and faceid ipadapter to sdxl_vit-h version
		Switch faceid lora to sdxl version
		Switch Image Upscale ControlNet Depth|Tile to sdxl version (in Upscale Sub Workflow JK🐉)
		Switch NNLatentUpscale version to SDXL
		Set Ultimate SD Upscale Tile size to 1024
		Switch Detailer's Add Detail Lora to SDXL version
		Switch Hand Fix Depth ControlNet version to SDXL
		Hand Fix MeshGraphhormer Hand Refiner resolution
		Use Load ControNet Model and set Union ControlNet type to load xinsir controlnet union in I/O Paint process
		Enable Black Pixel switch for Inpaint/Outpaint ControlNet in I/O Paint process
		(If it is SD15, choose the opposite)

	Other:
		1. Nodes State JK🐉 uses target nodes' id to control their active | mute | bypass mode. Need to update node_id_list if you make a copy.
		2. The order of Detailer Progress and Upscale Progress can be swapped. Please avoid to form loops. 
</details>

<details>
<summary><b>Explanation</b></summary>

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
</details>

## JK_workflow : img2mesh
<details>
<summary><b>Introduction</b></summary>

	Hotkey:
		\`: Main Workflow Control Pannels
	
	Workflow Control:
		Each img2mesh workflow contains several sub-workflows as the filename indicates.
		Each sub-workflow consists of one or more sub-steps.
		Each sub-step saves the result as images or meshes when it finishes generation.
		Each sub-step can switch from generation mode to loading mode.
		It's recommended to enable sub-step step by step and switch to loading mode after the generation.
	
	Other:
		TripoSR workflow is not included because it is straightforward.
		Triplane workflow is not included because it is straightforward.
</details>

<details>
<summary><b>Explanation</b></summary>

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh-types.png)
- Workflow breakdown: img2mesh types

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_CRM&Zero123plus&MVDream&CharacterGen-structure.png)
- Workflow breakdown: CRM&Zero123plus&MVDream&CharacterGen

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_Unique3D&Wonder3D&Era3D-structure.png)
- Workflow breakdown: JUnique3D&Wonder3D&Era3D

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_Zero123&SV3D-structure.png)
- Workflow breakdown: Zero123&SV3D

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_3DGS-structure.png)
- Workflow breakdown: 3DGS

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_CRM&Zero123plus&MVDream&CharacterGen.png)
- Workflow Control Panels: CRM&Zero123plus&MVDream&CharacterGen

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_Unique3D&Wonder3D&Era3D.png)
- Workflow Control Panels: Unique3D&Wonder3D&Era3D

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_Zero123&SV3D.png)
- Workflow Control Panels: Zero123&SV3D

![image](https://github.com/jakechai/ComfyUI-JakeUpgrade/blob/master/imgs/img2mesh_3DGS.png)
- Workflow Control Panels: 3DGS
</details>

## JakeUpgrade Nodes
<details>
<summary><b>Custom Nodes</b></summary>

	Misc Nodes
		SD1.5 Aspect Ratio JK🐉
		SDXL Aspect Ratio JK🐉
		SD3 Aspect Ratio JK🐉
    Reroute Nodes
		Reroute List JK🐉
		Reroute Ckpt JK🐉
		Reroute Vae JK🐉
		Reroute Sampler JK🐉
		Reroute Upscale JK🐉
		Reroute Resize JK🐉
		Reroute String JK🐉
    ControlNet Nodes
		Apply ControlNet JK🐉
		Multi-ControlNet Stack JK🐉
		Apply Multi-ControlNet JK🐉
		Apply Multi-ControlNet SD3 JK🐉
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
		Base Model Parameters SD3 JK🐉
		Refine Pipe JK🐉
		Refine Pipe Extract JK🐉
		Noise Injection Parameters JK🐉
		Noise Injection Pipe Extract JK🐉
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
		Remove Image Alpha JK🐉
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
		Noise Input Switch JK🐉
		Guider Input Switch JK🐉
		Sampler Input Switch JK🐉
		Sigmas Input Switch JK🐉
		Mesh Input Switch JK🐉
		Ply Input Switch JK🐉
		Orbit Pose Input Switch JK🐉
    ComfyMath Fix Nodes
		BoolToInt JK🐉
		IntToBool JK🐉
		BoolUnaryOp JK🐉
		BoolBinaryOp JK🐉
		StringBinaryCon JK🐉
		Prompt Combine JK🐉
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
</details>

<details>
<summary><b>Group Nodes</b></summary>

	Tools
		JK🐉::CLIPSegMask
		JK🐉::Image RemBG
		JK🐉::Image to Prompt (LLava Local)
		JK🐉::Image to Prompt Advanced (LLava Local)
		JK🐉::Pad Image for Outpainting
		JK🐉::SegAnythingMask		
	Workflow
		JK🐉::Concept
		JK🐉::Flux KSampler
		JK🐉::Flux KSampler Adv
		JK🐉::Inpaint Latent
		JK🐉::Inpaint Checkpoint
		JK🐉::Inpaint ControlNet			
		JK🐉::Outpaint Latent
		JK🐉::Outpaint Checkpoint
		JK🐉::Outpaint ControlNet
		JK🐉::txt2img
</details>

## Reference Custom Nodes
- [rgthree](https://github.com/rgthree/rgthree-comfy)
- [Comfyroll](https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes)
- [Efficiency Nodes](https://github.com/jags111/efficiency-nodes-comfyui)
- [ControlNet AUX](https://github.com/Fannovel16/comfyui_controlnet_aux)
- [Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)
- [Image Saver](https://github.com/giriss/comfy-image-saver)
- [Prompt Reader](https://github.com/receyuki/comfyui-prompt-reader-node)
- [ComfyMath](https://github.com/evanspearman/ComfyMath)
- [Embedding Picker](https://github.com/Tropfchen/ComfyUI-Embedding_Picker)
- [Layer Style](https://github.com/chflame163/ComfyUI_LayerStyle)

## Changelog
<details>
<summary><b>Previous Version</b></summary>
	
	- 2024-06-23 - v1.0.0	released.  
	- 2024-07-11 - v1.0.6	Noise Injection for Upscale Workflow.  
	- 2024-07-16 - v1.0.7	Single Image to Mesh Workflow updated.  
	- 2024-07-21 - v1.0.8	Orbit Poses Constant nodes added. 3 Image to Mesh Workflows updated.  
	- 2024-07-22 - v1.0.9	3DGS workflow added.  
	- 2024-07-24 - v1.1.0	img2mesh workflow updated. Craftsman Mesh added. 
				Three OrbitPoses nodes been added to 3D-Pack.  
	- 2024-07-31 - v1.1.1	Prompt Combine node added.  
	- 2024-08-03 - v1.1.2	Resize to Focus added to image2mesh workflow.  
	- 2024-08-21 - v1.1.3	Random Beats node added (not for AIGC).  
	- 2024-09-01 - v1.2.0	SD3 workflow added. Noise Injection (Inspire) added. 
				Refine, Upscale, and Detailer process major updated. 
				SD15 Hand Fix supports SDXL and SD3 workflow. 
				SDXL IPAdapter supports SD3 workflow. 
				NoiseInjection Component and workflow added.  
	- 2024-09-04 - v1.2.1	In/Out Paint ControlNet Component added. 
				Inpaint Module Workflow updated. 
				SD15|SDXL|SD3 Workflow updated. 
				Image Remove Alpha JK node added.  
	- 2024-09-05 - v1.2.2	Black Pixel switch added for Inpaint ControlNet Component following ControlNet Preprocessor AUX Custom Node's update.  
	- 2024-09-06 - v1.2.3	Refinement Noise Injection added. 
				txt2prompt and img2prompt workflow added. 
				img2prompt component added.  
	- 2024-09-07 - v1.2.4	img2mesh workflow doesn't need _JK.pack, so that doesn't need to install segment anything, VLM nodes, and IF AI tools.  
	- 2024-09-09 - v1.2.5	Clip l, clip g, t5xxl texture encode logic upgrade. 
				Clip l & g switch added. 
				Negative g switch added. 
				SDXL Clip Text Encode Target Resolution Scale added.  
	- 2024-09-10 - v1.2.6	detailer: add detail lora.  
	- 2024-09-11 - v1.2.7	Magic Photo Prompter added.  
	- 2024-09-13 - v1.2.8	Use Comfy UI default set union controlnet type to load xinsir sdxl controlnet union.  
				Remove Inspire Pack and WAS Nodes Suite in img2mesh workflows. 
				Group Node Image RemBG added, using InSPYReNet TransparentBG from Essentials to remove background and Image Composite Masked to add grayscale background.  
	- 2024-09-15 - v1.2.9	Inpaint Simple updated. Outpaint Simple added. 
				txt2img | img2img | inpaint workflow updated. 
				In/Out Paint to Refinement process added. 
				Upscale to Refinment process added.  
	- 2024-09-21 - v1.3.0	Inpaint/Outpaint Latent | Checkpoint | ControlNet group nodes updated. 
				Inpaint and txt2img/img2img workflows updated. 
				SD3/Flux Inpaint ControlNet added.  
	- 2024-09-24 - v1.3.1	Hand Fix Detailer upgrades, supports SD15 | SDXL | Flux. 
				SD3 Hand Fix need to choose SDXL models for the InstantX Depth ControlNet does not work properly. 
				Replace SD3 ControlNet Apply with new ControlNet Apply Node.  
	- 2024-09-25 - v1.3.2	AIO Preprocessor added for txt2img | img2img workflow.  
				Detailer, Upscale workflows updated. Refine workflow added.  
	- 2024-09-26 - v1.3.3	Latent Noise Mask switch added for Inpaint/Outpaint ControlNet. 
				Specified Dual Clip switch added for sdxl workflow.  
	- 2024-09-28 - v1.3.4	Hand Fix supports SD3 and Flux. Hand Fix module workflow added.
	- 2024-09-29 - v1.3.5	Inpaint Group Nodes upgrade, add more Image | Mask | Latent control.
	- 2024-10-01 - v1.3.6	Inpaint Group Nodes upgrade, change color grading method.
	- 2024-10-03 - v1.3.7	Remove Outpaint Pad Feathering.
</details>

- 2024-10-06 - v1.4.0	Replace Base Ipadapter simple with IPAdapter Style and Composition Transfer in SD15 and SDXL workflow.
			SD3 Aspect Ratio node and SD3 Base Model Parameter node added. 
			SD3 Api workflow added to make up the shorcomings of SD3 local deployment using Stability SD3 control and inpaint nodes.
- 2024-10-10 - v1.5.0	Flux KSampler and Flux Ksampler Adv group nodes added.
			Flux txt2img and img2img workflow added. Flux KSampler workflow added.
			Inpaint/Outpaint ControlNet and Checkpoint method order changed.
			Enchance and Resize Input Image added for img2img workflow.
			Noise | Guider | Sampler | Sigmas switch added.
- 2024-10-10 - v1.5.1	Fal LLM and VLM API added for prompt generation workflow and SAI API workfkow.
