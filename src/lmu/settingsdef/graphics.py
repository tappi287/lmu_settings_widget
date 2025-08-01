adjustable_graphics_settings = {
    "Track Detail": {
        "name": "Circuit Detail",
        "value": 2,
        "settings": (
            {"value": 0, "name": "Low"},
            {"value": 1, "name": "Medium"},
            {"value": 2, "name": "High"},
            {"value": 3, "name": "Full"},
        ),
    },
    "Player Detail": {
        "name": "Player Detail",
        "value": 3,
        "settings": (
            {"value": 0, "name": "Low"},
            {"value": 1, "name": "Medium"},
            {"value": 2, "name": "High"},
            {"value": 3, "name": "Full"},
        ),
    },
    "Opponent Detail": {
        "name": "Opponent Detail",
        "value": 2,
        "settings": (
            {"value": 0, "name": "Low"},
            {"value": 1, "name": "Medium"},
            {"value": 2, "name": "High"},
            {"value": 3, "name": "Full"},
        ),
    },
    "Texture Detail": {
        "name": "Texture Detail",
        "value": 3,
        "settings": (
            {"value": 0, "name": "Low"},
            {"value": 1, "name": "Medium"},
            {"value": 2, "name": "High"},
            {"value": 3, "name": "Full"},
        ),
    },
    "Texture Filter": {
        "name": "Texture Filter",
        "value": 4,
        "settings": (
            {"value": 0, "name": "Bilinear"},
            {"value": 1, "name": "Trilinear"},
            {"value": 2, "name": "x2 Anisotropic"},
            {"value": 3, "name": "x4 Anisotropic"},
            {"value": 4, "name": "x8 Anisotropic"},
            {"value": 5, "name": "x16 Anisotropic"},
        ),
    },
    "Special FX": {
        "name": "Special Effects",
        "value": 4,
        "settings": (
            {"value": 0, "name": "Off"},
            {"value": 1, "name": "Low", "perf": "G+0,18% C+0,00%"},
            {"value": 2, "name": "Medium"},
            {"value": 3, "name": "High"},
            {"value": 4, "name": "Ultra", "perf": "G+0,90% C+2,20%"},
        ),
    },
    "Shadows": {
        "name": "Shadows",
        "value": 3,
        "settings": (
            {"value": 0, "name": "Off"},
            {"value": 1, "name": "Low"},
            {"value": 2, "name": "Medium"},
            {"value": 3, "name": "High"},
            {"value": 4, "name": "Ultra"},
        ),
    },
    "Shadow Blur": {
        "name": "Shadow Blur",
        "value": 2,
        "settings": (
            {"value": 0, "name": "Off"},
            {"value": 1, "name": "Fast", "perf": "G+1,50% C+0,00%"},
            {"value": 2, "name": "Optimal", "perf": "G+3,0% C+0,50%"},
            {"value": 3, "name": "Quality", "perf": "G+8,5% C+1,00%"},
        ),
    },
    "Soft Particles": {
        "name": "Soft Particles",
        "value": 1,
        "settings": (
            {"value": 0, "name": "Off"},
            {"value": 1, "name": "Low", "desc": "Cheap soft edges"},
            {"value": 2, "name": "High", "desc": "Depth buffered soft edges", "perf": "G+0,57% C+2,57%"},
        ),
    },
    "Rain FX Quality": {
        "name": "Rain Drops",
        "value": 3,
        "settings": ({"value": 0, "name": "Low"}, {"value": 1, "name": "Medium"}, {"value": 2, "name": "High"}),
    },
    "Road Reflections": {
        "name": "Road Reflection",
        "value": 2,
        "settings": (
            {"value": 0, "name": "Low"},
            {"value": 1, "name": "Medium"},
            {"value": 2, "name": "High"},
            {"value": 3, "name": "Ultra"},
        ),
    },
    "Environment Reflections": {
        "name": "Environment Reflection",
        "value": 2,
        "settings": (
            {"value": 0, "name": "Low"},
            {"value": 1, "name": "Medium"},
            {"value": 2, "name": "High"},
            {"value": 3, "name": "Ultra"},
        ),
    },
    "Motion blur": {
        "name": "Motion blur",
        "value": 0,
        "settings": (
            {"value": 0, "name": "Off"},
            {"value": 1, "name": "Trackside only"},
            {"value": 2, "name": "On"},
        ),
    },
    "Max Visible Vehicles": {
        "name": "Visible Vehicles",
        "value": 12,
        "settings": ({"settingType": "range", "min": 5, "max": 105, "step": 1, "desc": "LMU default setting: 12"},),
    },
    "Screen Space Ambient Occlusion": {
        "name": "Ambient Occlusion",
        "value": True,
        "settings": (
            {"value": False, "name": "Disabled"},
            {
                "value": True,
                "name": "Enabled [Default]",
                "desc": "Enable Screen Space Ambient Occlusion",
            },
        ),
    },
}
view_settings = {
    "Stabilize Horizon": {
        "name": "Stabilize Horizon",
        "value": 1,
        "settings": (
            {"value": 0, "name": "Off"},
            {"value": 1, "name": "Low"},
            {"value": 2, "name": "Medium"},
            {"value": 3, "name": "High"},
        ),
    },
    "Exaggerate Yaw": {
        "name": "Exaggerate Yaw",
        "value": -0.8,
        "settings": (
            {
                "settingType": "range",
                "min": -1.0,
                "max": 1.0,
                "step": 0.01,
                "display": "floatpercent",
                "desc": "Visually exaggerates the heading angle of the vehicle "
                'by rotating the head (which may improve "feel")',
            },
        ),
    },
    "Lookahead Angle": {
        "name": "Lookahead Angle",
        "value": 0.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "display": "floatpercent",
                "desc": 'Angle to look ahead (yaw) with steering in radians"',
            },
        ),
    },
    "Head Physics": {
        "name": "Head Physics",
        "value": 1.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "display": "floatpercent",
                "desc": "Fraction of head physics movement applied to " "cockpit view (position AND rotation)",
            },
        ),
    },
    "Steering Wheel": {
        "name": "Steering Wheel",
        "value": 0,
        "settings": (
            {"value": 0, "name": "On [Default]", "desc": "Moving steering wheel and arms"},
            {"value": 1, "name": "Fixed", "desc": "Non-moving steering wheel or arms"},
            {
                "value": 2,
                "name": "Off",
                "desc": "No steering wheel or arms (in cockpit only " "while player-controlled)",
            },
            {"value": 3, "name": "No arms", "desc": "Moving steering wheel but no arms"},
        ),
    },
    "Vertical FOV Degrees": {
        "name": "Vertical FOV",
        "value": 9,
        "settings": (
            {
                "settingType": "range",
                "min": 9,
                "max": 100,
                "step": 1,
                "desc": "9 means use individual default value for each vehicle. "
                "Vertical field of view in "
                "degrees(horizontal is calculated based on aspect ratio).",
            },
        ),
    },
}
vr_graphics_settings = {
    "VR HUD Scale": {
        "name": "HUD Scale",
        "value": 1.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.1,
                "max": 2.0,
                "step": 0.01,
                "display": "floatdecimal",
                "desc": "Scale of the VR UI HUD screen",
            },
        ),
    },
    "VR Menu Scale": {
        "name": "Menu Scale",
        "value": 1.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.1,
                "max": 2.0,
                "step": 0.01,
                "display": "floatdecimal",
                "desc": "Scale of menus in VR",
            },
        ),
    },
    "VR IPD Scale": {
        "name": "World Scale",
        "value": 1.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.5,
                "max": 2.0,
                "step": 0.01,
                "display": "floatdecimal",
                "desc": "VR IPD Scale: Adjusts IPD distance between eyes. 1.0 = default IPD distance, as reported by the HMD, below 1.0 = reduce, above 1.0 = increase",
            },
        ),
    },
    "VR HUD Depth": {
        "name": "HUD Depth",
        "value": 0.5,
        "settings": (
            {
                "settingType": "range",
                "min": 0.01,
                "max": 1.0,
                "step": 0.01,
                "display": "floatdecimal",
                "desc": "Depth of the VR UI HUD screen",
            },
        ),
    },
    "VR Menu Depth": {
        "name": "Menu Depth",
        "value": 0.5,
        "settings": (
            {
                "settingType": "range",
                "min": 0.01,
                "max": 1.0,
                "step": 0.01,
                "display": "floatdecimal",
                "desc": "Depth of menus in VR",
            },
        ),
    },
    "VR Projection Mode": {
        "name": "Projection Mode",
        "value": 0,
        "settings": (
            {
                "value": 0,
                "name": "Default",
            },
            {
                "value": 1,
                "name": "Not in-plane Displays",
                "desc": "VR Projection Mode: 0 = default, 1 = not in-plane displays HMDs",
            },
        ),
    },
    "VR Enable Hidden Area Mask": {
        "name": "Hidden Area Mask",
        "value": True,
        "settings": (
            {"value": False, "name": "Disabled"},
            {
                "value": True,
                "name": "Enabled [Default]",
                "desc": "Enable VR hidden area mask, may improve VR performance.",
            },
        ),
    },
}

advanced_settings = {
    "Transparency AA": {
        "name": "Transparency AA",
        "value": True,
        "settings": (
            {"value": False, "name": "Disabled"},
            {"value": True, "name": "Enabled [Default]", "desc": "Soften edges around alpha test objects"},
        ),
    },
    "Texture Sharpening": {
        "name": "Texture Sharpening",
        "value": 5,
        "settings": (
            {
                "value": 0,
                "name": "Off",
            },
            {"value": 1, "name": "+2.0", "desc": "Sharpen textures using MIP LOD bias (very blurry)"},
            {"value": 2, "name": "+1.0", "desc": "Sharpen textures using MIP LOD bias (blurry)"},
            {"value": 3, "name": "-1.0", "desc": "Sharpen textures using MIP LOD bias (sharp)"},
            {"value": 4, "name": "-2.0", "desc": "Sharpen textures using MIP LOD bias (very sharp)"},
            {"value": 5, "name": "Auto [Default]"},
        ),
    },
    "Heat FX Fade Speed": {
        "name": "Heat FX Fade Speed",
        "value": 30,
        "settings": (
            {
                "value": 30,
                "name": "30 [Default]",
                "desc": "Speed at which exhaust heat effects reduce " "by half (0 to completely disable)",
            },
            {"value": 0, "name": "0", "desc": "Fixes visual artefact bubble behind certain cars in VR."},
        ),
    },
    "Rearview Particles": {
        "name": "Rearview Particles",
        "value": True,
        "settings": (
            {"value": False, "name": "Disabled"},
            {
                "value": True,
                "name": "Enabled [Default]",
                "desc": "Show particles like rain spray in the rear view mirror",
            },
        ),
    },
    "Rearview_Back_Clip": {
        "name": "Rearview Back Clip",
        "value": 0,
        "settings": (
            {
                "settingType": "range",
                "min": 0,
                "max": 250,
                "step": 20,
                "desc": "Back plane distance(view distance) for mirror " "(0.0 = use default for scene)",
            },
        ),
    },
    "Rearview Driving": {
        "name": "Rearview Driving",
        "value": True,
        "settings": (
            {"value": False, "name": "Off", "desc": "Applies to in-game nosecam, cockpit, and TV cockpit"},
            {"value": True, "name": "On"},
        ),
    },
    "Rearview Onboard": {
        "name": "Rearview Onboard",
        "value": False,
        "settings": (
            {"value": False, "name": "Off", "desc": "Applies to in-game onboard cams"},
            {"value": True, "name": "On"},
        ),
    },
    "Rearview Swingman": {
        "name": "Rearview Swingman",
        "value": True,
        "settings": (
            {"value": False, "name": "Off", "desc": "Applies to in-game Swingman Cam"},
            {"value": True, "name": "On"},
        ),
    },
    "Sun Occlusion": {
        "name": "Sun Occlusion",
        "value": False,
        "settings": (
            {"value": False, "name": "Off [Default]"},
            {"value": True, "name": "On", "desc": "Sunlight is affected by cloud cover"},
        ),
    },
    "Max Framerate": {
        "name": "Max Framerate",
        "value": 0,
        "settings": (
            {"settingType": "range", "min": 0, "max": 288, "step": 1, "desc": "0 to disable, LMU default setting: 0"},
        ),
    },
    "Max Headlights": {
        "name": "Max Headlights",
        "value": 256,
        "settings": (
            {
                "settingType": "range",
                "min": 0,
                "max": 256,
                "step": 1,
                "desc": "Max headlights visible relative to your car. (Note current system only allows upto 20)",
            },
        ),
    },
    "Headlights On Cars": {
        "name": "Headlights On Cars",
        "value": True,
        "settings": (
            {"value": False, "name": "Off"},
            {"value": True, "name": "On [Default]", "desc": "Headlights illuminate other cars."},
        ),
    },
}

adjustable_video_settings = {
    "Launch": {
        "name": "Launch",
        "value": 1,
        "_type": int,
        "desc": "Choose how this widget should launch LMU " "if this preset is selected.",
        "hidden": False,
        "settings": (
            {"value": 1, "name": "via Executable (Desktop)"},
            {"value": 3, "name": "via Executable (VR)"},
            {"value": 0, "name": "via Steam (Desktop)"},
            {"value": 2, "name": "via Steam (VR)"},
        ),
    },
    "MSAA": {
        "name": "Anti Aliasing",
        "value": 0,
        "_type": int,
        "settings": (
            {"value": 0, "name": "Off"},
            {"value": 2, "name": "2x MSAA", "desc": "2x [2x Multisampling]"},
            {"value": 4, "name": "4x MSAA", "desc": "4x [4x Multisampling]"},
            {"value": 8, "name": "8x MSAA", "desc": "8x [8x Multisampling]"},
        ),
    },
    "EPostProcessingSettings": {
        "name": "Post Effects",
        "value": 1,
        "_type": int,
        "settings": (
            {"value": 1, "name": "Low"},
            {"value": 2, "name": "Medium"},
            {"value": 3, "name": "High"},
        ),
    },
    "UseFXAA": {
        "name": "FXAA",
        "value": 0,
        "_type": int,
        "desc": "Can not be used with FSAA. You should prefer FSAA " "whenever possible.",
        "settings": (
            {"value": 0, "name": "Off"},
            {"value": 1, "name": "On", "desc": "Cheap post processing filter to smooth " "high contrast edges."},
        ),
    },
}
resolution_video_settings = {
    "WindowedMode": {
        "name": "Windowed Mode",
        "value": None,
        "hidden": True,
        "settings": ({"value": 0, "name": "Fullscreen"}, {"value": 1, "name": "Windowed"}),
    },
    "Borderless": {
        "name": "Borderless",
        "value": None,
        "hidden": True,
        "settings": ({"value": 0, "name": "Windowed"}, {"value": 1, "name": "Borderless"}),
    },
    "VideoMode": {"name": "Resolution", "value": None, "hidden": True, "settings": ({"value": 125, "name": "FullHD"},)},
    "VideoRefresh": {
        "name": "Refresh Rate",
        "value": None,
        "hidden": True,
        "settings": ({"value": 1, "name": "60Hz"},),
    },
    "VideoResW": {
        "name": "Resolution Width",
        "value": None,
        "hidden": True,
        "settings": ({"value": 1920, "name": "FullHD"},),
    },
    "VideoResH": {
        "name": "Resolution Height",
        "value": None,
        "hidden": True,
        "settings": ({"value": 1080, "name": "FullHD"},),
    },
    "VideoRefreshRate": {
        "name": "Video Refresh Rate",
        "value": None,
        "hidden": True,
        "settings": ({"value": 144, "name": "144Hz"},),
    },
}
reshade_settings = {
    "use_reshade": {
        "name": "Use VRToolkit+ReShade",
        "value": False,
        "desc": "The VRToolkit is a modular shader created for ReShade to enhance the clarity & sharpness "
        "in VR to get most out of your HMD while keeping the performance impact minimal.",
        "settings": (
            {"value": False, "name": "Disabled"},
            {"value": True, "name": "Enabled"},
        ),
    },
    "use_openxr": {
        "name": "Use OpenXR",
        "value": False,
        "desc": "Weather to inject ReShade via it's OpenXR API Layer or it's DLL hook. "
        "If you run in Desktop-Mode leave disabled. If you use "
        "Virtual-Reality / OpenXR set to enabled.",
        "settings": (
            {"value": False, "name": "Disabled"},
            {"value": True, "name": "Enabled"},
        ),
    },
    "VRT_SHARPENING_MODE": {
        "name": "Sharpening Mode",
        "value": 1,
        "desc": "Configures the sharpening/clarity modes",
        "settings": (
            {"value": 0, "name": "Disabled"},
            {"value": 1, "name": "FAS [Default]", "desc": "Use Filmic anamorph sharpening"},
            {"value": 2, "name": "AMD CAS", "desc": "Use AMD Fidelity FX contrast adaptive sharpening (CAS)"},
        ),
    },
    "VRT_ANTIALIASING_MODE": {
        "name": "Anti Aliasing Mode",
        "value": 0,
        "desc": "Anti aliasing to reduce aliasing/shimmering. This helps to further smoothen out "
        "the image after MSAA has done most of the work",
        "settings": (
            {"value": 0, "name": "Disabled [Default]"},
            {"value": 1, "name": "FXAA", "desc": "Experimental"},
        ),
    },
    "VRT_COLOR_CORRECTION_MODE": {
        "name": "Color Correction Mode",
        "value": 0,
        "desc": "Configures the color correction modes",
        "settings": (
            {"value": 0, "name": "Disabled [Default]"},
            {"value": 1, "name": "LUT", "desc": "Uses a LUT (Look up table) for specialized and complex corrections."},
            {"value": 2, "name": "Contrast & Saturation", "desc": "Adjust Contrast and Saturation"},
        ),
    },
    "VRT_DITHERING": {
        "name": "Use Dithering",
        "value": 0,
        "desc": "Dithering Noise to reduce color banding on gradients ",
        "settings": (
            {"value": 0, "name": "Disabled [Default]"},
            {
                "value": 1,
                "name": "Enabled",
                "desc": "Enable dithering that adds noise to the image to smoothen out gradients",
            },
        ),
    },
    "VRT_USE_CENTER_MASK": {
        "name": "Use Center Mask",
        "value": 1,
        "desc": "Masks the center of the screen with a circle to reduce pixel count that "
        "is processed by the shaders [DX10 or higher]",
        "settings": (
            {"value": 0, "name": "Disabled"},
            {
                "value": 1,
                "name": "Enabled [Default]",
                "desc": "Uses circular mask to improve shader performance on games rendering on " "DX10 or higher",
            },
        ),
    },
}
clarity_settings = {
    "use_clarity": {
        "name": "Use Clarity2.fx",
        "value": False,
        "desc": "GPU intensive shader to increase image clarity.",
        "settings": (
            {"value": False, "name": "Disabled"},
            {"value": True, "name": "Enabled"},
        ),
    },
    "ClarityRGBMode": {
        "name": "RGB Mode",
        "value": 0,
        "desc": "Runs Clarity in RGB instead of luma.",
        "settings": ({"value": 0, "name": "Luma [Default]"}, {"value": 1, "name": "RGB"}),
    },
    "UseClarityDebug": {
        "name": "Debug Mode",
        "value": 0,
        "desc": "Activates debug options.",
        "settings": ({"value": 0, "name": "Off [Default]"}, {"value": 1, "name": "On"}),
    },
}
reshade_mask = {
    "CircularMaskSize": {
        "name": "Circle Radius",
        "value": 0.30,
        "settings": (
            {
                "settingType": "range",
                "min": 0.01,
                "max": 1.0,
                "step": 0.01,
                "desc": "Keep the radius as small as possible to conserve GPU time, but as well not to "
                "small to not loose sharpness. In addition some HMDs need an offset correction "
                "like the Pimax to fit the sweet spot better. Recommended: "
                "Valve Index: 0.30-0.35, Oculus Quest1: 0.30 to 0.35, HP G1 & G2: 0.41 to 0.46, "
                "Pimax 5k Large FOV, No PP: +- 0.75 [Default 0.30]",
            },
        ),
    },
    "CircularMaskSmoothness": {
        "name": "Mask Smoothness",
        "value": 5.0,
        "settings": (
            {
                "settingType": "range",
                "min": 1.0,
                "max": 10.0,
                "step": 0.01,
                "desc": "Increases the smoothness of the circular mask to allow smaller masks "
                "while reducing the prominence of the edge [Default 5.0]",
            },
        ),
    },
    "CircularMaskHorizontalOffset": {
        "name": "Horizontal Offset",
        "value": 0.30,
        "settings": (
            {
                "settingType": "range",
                "min": 0.30,
                "max": 0.5,
                "step": 0.01,
                "desc": "Adjusts the mask offset from the center horizontally " "[Default 0.30]",
            },
        ),
    },
}
reshade_dither = {
    "DitheringStrength": {
        "name": "Dithering Strength",
        "value": 0.375,
        "settings": (
            {
                "settingType": "range",
                "min": 0.00,
                "max": 1.0,
                "step": 0.001,
            },
        ),
    },
}
reshade_fas = {
    "FAS_Strength": {
        "name": "Strength",
        "value": 125.0,
        "settings": ({"settingType": "range", "min": 0.0, "max": 250.0, "step": 1.0, "desc": "[Default 125]"},),
    },
    "FAS_Radius": {
        "name": "Radius",
        "value": 0.10,
        "settings": (
            {
                "settingType": "range",
                "min": 0.00,
                "max": 2.00,
                "step": 0.01,
                "desc": "High-pass cross offset in pixels [Default 0.10]",
            },
        ),
    },
    "FAS_Clamp": {
        "name": "Clamping",
        "value": 0.525,
        "settings": ({"settingType": "range", "min": 0.500, "max": 1.00, "step": 0.001, "desc": "[Default 0.525]"},),
    },
}
reshade_cas = {
    "CAS_Contrast": {
        "name": "Contrast Adaption",
        "value": 0.00,
        "settings": (
            {
                "settingType": "range",
                "min": 0.00,
                "max": 1.00,
                "step": 0.01,
                "desc": "Adjusts the range the shader adapts to high contrast (0 is not all the way off). "
                "Higher values = more high contrast sharpening. [Default 0.0]",
            },
        ),
    },
    "CAS_Sharpening": {
        "name": "Sharpening",
        "value": 2.5,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 5.0,
                "step": 0.01,
                "desc": "Adjusts sharpening intensity by averaging the original pixels to the sharpened "
                "result. 1.0 is the unmodified default. [Default 2.5]",
            },
        ),
    },
    "CAS_Contrast_Clamp": {
        "name": "Contrast Clamping",
        "value": 0.10,
        "settings": (
            {
                "settingType": "range",
                "min": 0.00,
                "max": 1.00,
                "step": 0.01,
                "desc": "Limits the bright & contrasty parts from being sharpened. Lower the value to "
                "reduce shimmering on bright lines",
            },
        ),
    },
}
reshade_lut = {
    "LUT_AmountChroma": {
        "name": "LUT chroma amount",
        "value": 1.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "desc": "Intensity of color/chroma change of the LUT. [Default 1.0]",
            },
        ),
    },
    "LUT_AmountLuma": {
        "name": "LUT luma amount",
        "value": 1.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "desc": "Intensity of luma change of the LUT. [Default 1.0]",
            },
        ),
    },
    "LUT_TextureName": {
        "name": "LUT",
        "value": '"lut.png"',
        "settings": (
            {"value": '"lut.png"', "name": "No Correction [Default]"},
            {
                "value": '"lmu_ToneUpDay.png"',
                "name": "LMU Tone Up Day",
                "desc": "LUT trying to accommodate for the relative low exposure in v0.4",
            },
            {
                "value": '"lmu_DayTone.png"',
                "name": "LMU Day",
                "desc": "Increase exposure for v0.4 and tone-map highlights",
            },
            {
                "value": '"Super_ToneDownDay.png"',
                "name": "Super Tone Down Day",
                "desc": "LUT trying to restore some highlights from super bright specular road "
                "reflections at daylight. Desaturated Reds for Pimax Crystal Super Panel.",
            },
            {
                "value": '"rF2_nonPBRmodDay1.png"',
                "name": "Non PBR Mod 1",
                "desc": "LUT trying to restore some highlights from super bright specular road "
                "reflections on non-PBR mod tracks at daylight. "
                "Also desaturates reds and greens. Lower Contrast.",
            },
            {
                "value": '"rF2_nonPBRmodDay2.png"',
                "name": "Non PBR Mod 2",
                "desc": "LUT trying to restore some highlights from super bright specular road "
                "reflections on non-PBR mod tracks at daylight. "
                "Also desaturates reds and greens. Medium Contrast.",
            },
            {
                "value": '"rF2_ToneDownDay.png"',
                "name": "Tone Down Day",
                "desc": "LUT trying to restore some highlights from super bright specular road "
                "reflections on PBR tracks at daylight. ",
            },
            {
                "value": '"lut_ams.png"',
                "name": "Retrolux AMS",
                "desc": "LUT Preset from Retrolux Reshade Automobilista",
            },
            {
                "value": '"lut_gtr2.png"',
                "name": "Retrolux GTR2",
            },
            {
                "value": '"lut_rbr.png"',
                "name": "Retrolux RBR",
            },
            {
                "value": '"lut_filmic_basic.png"',
                "name": "Retrolux Filmic Basic",
            },
            {
                "value": '"lut_provia.png"',
                "name": "Retrolux Provia",
            },
            {
                "value": '"lut_technicolor.png"',
                "name": "Retrolux Technicolor",
            },
        ),
    },
}
reshade_cc = {
    "CS_Contrast": {
        "name": "Contrast",
        "value": 0.00,
        "settings": (
            {
                "settingType": "range",
                "min": -1.00,
                "max": 1.00,
                "step": 0.01,
                "desc": "The amount of contrast you want.",
            },
        ),
    },
    "CS_Saturation": {
        "name": "Saturation",
        "value": 1.0,
        "settings": (
            {"settingType": "range", "min": 0.0, "max": 2.0, "step": 0.01, "desc": "Adjust saturation [Default 1.0]"},
        ),
    },
}
reshade_aa = {
    "Subpix": {
        "name": "Subpix",
        "value": 1.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "desc": "Amount of sub-pixel aliasing removal. Higher values makes the image "
                "softer/blurrier. [Default 1.0]",
            },
        ),
    },
    "EdgeThreshold": {
        "name": "Edge Detection Threshold",
        "value": 0.125,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 1.0,
                "step": 0.005,
                "desc": "The minimum amount of local contrast required to apply algorithm. " "[Default 0.125]",
            },
        ),
    },
    "EdgeThresholdMin": {
        "name": "Darkness Threshold",
        "value": 0.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "desc": "Pixels darker than this are not processed in order to " "increase performance. [Default 0.0]",
            },
        ),
    },
}
reshade_clarity = {
    "ClarityRadiusTwo": {
        "name": "Radius",
        "value": 1,
        "desc": "Higher values will increase the radius of the effect.",
        "settings": (
            {"value": 0, "name": "0"},
            {"value": 1, "name": "1"},
            {"value": 2, "name": "2"},
            {"value": 3, "name": "3"},
            {"value": 4, "name": "4"},
        ),
    },
    "ClarityOffsetTwo": {
        "name": "Offset",
        "value": 2.0,
        "settings": (
            {
                "settingType": "range",
                "min": 1.0,
                "max": 5.0,
                "step": 1.0,
                "desc": "Additional adjustment for the blur radius. Increasing " "the value will increase the radius.",
            },
        ),
    },
    "ClarityBlendModeTwo": {
        "name": "Blend Mode",
        "value": 2,
        "desc": "Blend modes determine how the clarity mask is applied to the original image",
        "settings": (
            {"value": 0, "name": "Soft Light"},
            {"value": 1, "name": "Overlay"},
            {"value": 2, "name": "Hard Light [Default]"},
            {"value": 3, "name": "Multiply"},
            {"value": 4, "name": "Vivid Light"},
            {"value": 5, "name": "Linear Light"},
            {"value": 6, "name": "Addition"},
        ),
    },
    "ClarityBlendIfDarkTwo": {
        "name": "Blend If Dark",
        "value": 50,
        "settings": (
            {
                "settingType": "range",
                "min": 0,
                "max": 255,
                "step": 1,
                "desc": "Any pixels below this value will be excluded from the effect. Set to 50 to "
                "target mid-tones.",
            },
        ),
    },
    "ClarityBlendIfLightTwo": {
        "name": "Blend If Light",
        "value": 205,
        "settings": (
            {
                "settingType": "range",
                "min": 0,
                "max": 255,
                "step": 1,
                "desc": "Any pixels above this value will be excluded from the effect. "
                "Set to 205 to target mid-tones.",
            },
        ),
    },
    "BlendIfRange": {
        "name": "Blend If Range",
        "value": 0.2,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "desc": "Adjusts the range of the BlendIfMask.",
            },
        ),
    },
    "ClarityStrengthTwo": {
        "name": "Strength",
        "value": 0.400,
        "settings": (
            {
                "settingType": "range",
                "min": 0.00,
                "max": 1.00,
                "step": 0.005,
                "desc": "Adjusts the strength of the effect",
            },
        ),
    },
    "ClarityDarkIntensityTwo": {
        "name": "Clarity Dark Intensity",
        "value": 0.400,
        "settings": (
            {
                "settingType": "range",
                "min": 0.00,
                "max": 1.00,
                "step": 0.005,
                "desc": "Adjusts the strength of dark halos.",
            },
        ),
    },
    "ClarityLightIntensityTwo": {
        "name": "Clarity Light Intensity",
        "value": 0.000,
        "settings": (
            {
                "settingType": "range",
                "min": 0.00,
                "max": 1.00,
                "step": 0.005,
                "desc": "Adjusts the strength of light halos.",
            },
        ),
    },
    "DitherStrength": {
        "name": "Dither Strength",
        "value": 1.0,
        "settings": (
            {
                "settingType": "range",
                "min": 0.0,
                "max": 10.0,
                "step": 0.1,
                "desc": "Adds dithering to the ClarityMask to help reduce banding. "
                "Leave at 0 and use the optimized VRToolKit Shader instead.",
            },
        ),
    },
    "MaskContrast": {
        "name": "Mask Contrast",
        "value": 0.00,
        "settings": (
            {
                "settingType": "range",
                "min": 0.00,
                "max": 1.0,
                "step": 0.01,
                "desc": "Additional adjustment for the blur radius. Increasing the value will " "increase the radius.",
            },
        ),
    },
}
