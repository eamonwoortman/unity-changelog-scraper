
# define transforms
transformers = {
    'category_types': [
        { "pattern": r"(?i)(asset\s(Import.*|pipeline|management))|(^importer|^importing)", "replacement": "Asset Importer" },
        { "pattern": r"^(?i)(api\s?updater)$", "replacement": "API Updater" },
        { "pattern": r"^(?i)(assets?\sloading)$", "replacement": "Asset Loading" },
        { "pattern": r"^(?i)(asset\s?database)$", "replacement": "Asset Database" },
        { "pattern": r"^(?i)(asset\s?bundles?)$", "replacement": "Asset Bundles" },
        { "pattern": r"^(?i)(apple\s?tv)$", "replacement": "Apple TV" },
        { "pattern": r"^(?i)(blackberry)$", "replacement": "BlackBerry" },
        { "pattern": r"^(?i)(bug\s?reporter)$", "replacement": "Bug Reporter" },
        { "pattern": r"^(?i)(build\s?(pipeline|management|player|system)?)$", "replacement": "Build Pipeline" },
        { "pattern": r"^(?i)(cache\s?server)$", "replacement": "Cache Server" },
        { "pattern": r"^(?i)(cloud\s?services?)$", "replacement": "Cloud Services" },
        { "pattern": r"^(?i)(code\s?editors?)$", "replacement": "Code Editors" },
        { "pattern": r"^(?i)(collab|Collaborate|Collaboration)$", "replacement": "Collaborate" },
        { "pattern": r"^(?i)(deployment(\smanagement)?)$", "replacement": "Deployment Management" },
        { "pattern": r"^(D3D|D3D11|Direct3D\s?11|DX11|DirectX\s11)$", "replacement": "DirectX 11" },
        { "pattern": r"^(D3D12|DirectX\s?12|DX12)$", "replacement": "DirectX 12" },
        { "pattern": r"^(D3D9)$", "replacement": "DirectX 9" },
        { "pattern": r"^(?i)(editor\s?analytics)$", "replacement": "Editor Analytics" },
        { "pattern": r"^(?i)(frame\s?debugger)$", "replacement": "Frame Debugger" },
        { "pattern": r"^(Home(\s?Window)?)$", "replacement": "Home Window" },
        { "pattern": r"^(Input(\s?System)?)$", "replacement": "Input System" },
        { "pattern": r"^(?i)(internal)$", "replacement": "Internal" },
        { "pattern": r"^(?i)(Inspector(\s?(Framework|functionality))?)$", "replacement": "Inspector Framework" },
        { "pattern": r"^(?i)(il2cpp)$", "replacement": "IL2CPP" },
        { "pattern": r"^(Install(ers?)?)$", "replacement": "Installer" },
        { "pattern": r"^(Memory(\s?Profiler)?)$", "replacement": "Memory Profiler" },
        { "pattern": r"^(?i)(macos)$", "replacement": "MacOS" },
        { "pattern": r"^(OS\s?X)$", "replacement": "OSX" },
        { "pattern": r"^(OS\s?X\sEditor)$", "replacement": "OSX Editor" },
        { "pattern": r"^(?i)(os\s?x\s(standalone|player)?)$", "replacement": "OSX Standalone" },
        { "pattern": r"^(?i)opengl\score$", "replacement": "OpenGL Core" },
        { "pattern": r"^(?i)(opengl\s?es)$", "replacement": "OpenGL ES" },
        { "pattern": r"^(?i)(package manager|packman)$", "replacement": "Package Manager" },
        { "pattern": r"^(?i)(particle system|particles)$", "replacement": "Particle System" },
        { "pattern": r"^(Performance Reporting|Performance Reporting Service)$", "replacement": "Performance Reporting" },
        { "pattern": r"^(?i)((physics\s?2d)|(Phyics2D|Physic 2D))$", "replacement": "Physics 2D" },
        { "pattern": r"^(?i)(prefabs?)$", "replacement": "Prefabs" },
        { "pattern": r"^(?i)(ps4)$", "replacement": "PS4" },
        { "pattern": r"^(?i)(uGUI)$", "replacement": "UGUI" },
        { "pattern": r"^(?i)(samsung\s?tv)$", "replacement": "Samsung TV" },
        { "pattern": r"^(?i)(shadergraph)$", "replacement": "ShaderGraph" },
        { "pattern": r"^(?i)(scene\s?manager)$", "replacement": "Scene Manager" },
        { "pattern": r"^(?i)(scene\s?management)$", "replacement": "Scene Management" },
        { "pattern": r"^(?i)(texture\s?importer)$", "replacement": "Texture Importer" },
        { "pattern": r"^(?i)(unett?)$", "replacement": "UNET" },
        { "pattern": r"^(?i)((unity test runner)|(testing))$", "replacement": "Unity Test Runner" },
        { "pattern": r"^(?i)(universal\swindows\sapps)$", "replacement": "Universal Windows Apps" },
        { "pattern": r"^(?i)(version\s?control)$", "replacement": "Version Control" },
        { "pattern": r"^(?i)((visual\seffects?)|(VFX\s?(graph)?))$", "replacement": "VFX" },
        { "pattern": r"^(?i)(visual\s?studio(\sintegration)?)", "replacement": "Code Editors" },
        { "pattern": r"^(?i)(ios)$", "replacement": "IOS" },
        { "pattern": r"^(?i)(xr)$", "replacement": "XR" },
        { "pattern": r"^(?i)(xbox\s?one)$", "replacement": "Xbox One" },
    ]
}

# main options dict
options = {
    'transformers': transformers,
}
