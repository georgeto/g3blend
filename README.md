# Introduction
g3blend is a Blender addon to import and export Gothic 3 actors (`.xact`) and animations (`.xmot`).

It is currently in an early beta phase, so expect limitations in terms usability and functionality.
The import of `xact` and `xmot`, as well as the export of new or modified animations as `xmot` should work.

# Installation
## Install from release zip
Install the [latest release zip](https://github.com/georgeto/g3blend/releases/latest) via `Edit->Preferences->Add-ons->Install`.
Make sure to enable the addon after install.

## Install from source
Pack the [g3blend](./g3blend) folder into a zip file.
Then follow the same steps as in [Install from release zip](#install-from-release-zip).

## Manual install from source
Alternatively install from source by copying the [g3blend](./g3blend) folder to `c:\Users\<User Name>\AppData\Roaming\Blender Foundation\Blender\<Blender Version>\scripts\addons\`.
Make sure to enable the addon after install.

# Usage
- Import `xact` via `File->Import->Gothic 3 Actor`.
- Import `xmot` via  `File->Import->Gothic 3 Motion`.
- Emport `xmot` via  `File->Export->Gothic 3 Motion`.

## Frame effects
When an animation is imported/exported, its frame effects are stored in/retrieved from a custom property named `frame_effects` in the corresponding action object.
The `frame_effects` custom property is a dictionary where each entry consists of a frame number (key) and an effect name (value).
It can be edited in the `Custom Properties` section of the action in Blender's Action Editor view.

## World Import

The *World Import* option allows you to import parts of a Gothic 3 world directly into Blender based on entity data.

### Requirements

To use this feature, you need the following:

- **entities.json**  
  A file containing world entity data.  
  You can generate this file using the *"List entities"* script in [g3dit](https://forum.worldofplayers.de/forum/threads/1330059-Tool-g3dit-Weltdaten-Editor).

- **Resource Path**  
  A directory containing all Gothic 3 resources.  
  This should include the extracted contents of the `.pak` files from the Gothic 3 `Data` directory.

### Import Settings

When using *World Import*, configure the following options:

- **Import Position**  
  The base position used to determine which entities will be imported.

- **Import Radius**  
  Defines the size of the import area around the base position.

- **Ignore Y**  
  If enabled, the Y coordinate (vertical axis) is ignored during filtering.  
  - Enabled → The import area is a **circle** (2D filtering).  
  - Disabled → The import area is a **sphere** (3D filtering).

### Step-by-Step Usage

1. Extract the Gothic 3 `.pak` files into a directory (your resource path).
2. Configure the resource directory created in step as the (secondary) data directory in *g3dit* (`File->Settings`).
3. Use *g3dit* to run the **"List entities"** script and export an `entities.json`.
4. In Blender, open the import menu and select **World Import**.
5. Select your `entities.json` file.
6. Set the **Resource Path** to your extracted data directory.
7. Enter the desired **Import Position**.
8. Set an **Import Radius**.
9. (Optional) Enable or disable **Ignore Y** depending on whether you want 2D or 3D filtering.
10. Run the import.

# Demo
Futuristic doors in Gothic 3...

[Futuristic door example](https://github.com/georgeto/g3blend/assets/9250103/566755c9-1cc9-40cc-a89f-fd79012edbf5)

Scavenger is not convinced by this innovation!

[Scavenger not convinced](https://github.com/georgeto/g3blend/assets/9250103/0bb1a116-454b-4e1d-9cc6-bb423442dc6d)

# Credits
* Auronen
* [io_scene_fbx](https://projects.blender.org/blender/blender-addons/src/branch/main/io_scene_fbx)
* KrxImpExp
* [Kaitai Struct](https://doc.kaitai.io/)
