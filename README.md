# g3blend
g3blend is a Blender addon to import and export Gothic 3 actors (`.xact`) and animations (`.xmot`).

It is currently in an early beta phase, so expect limitations in terms usability and functionality.
The import of `xact` and `xmot`, as well as the export of new or modified animations as `xmot` should work.

## Installation
### Install from release zip
Install the [latest release zip](https://github.com/georgeto/g3blend/releases/latest) via `Edit->Preferences->Add-ons->Install`.
Make sure to enable the addon after install.

### Install from source
Pack the [g3blend](./g3blend) folder into a zip file.
Then follow the same steps as in [Install from release zip](#install-from-release-zip).

### Manual install from source
Alternatively install from source by copying the [g3blend](./g3blend) folder to `c:\Users\<User Name>\AppData\Roaming\Blender Foundation\Blender\<Blender Version>\scripts\addons\`.
Make sure to enable the addon after install.

## Usage
- Import `xact` via `File->Import->Gothic 3 Actor`.
- Import `xmot` via  `File->Import->Gothic 3 Motion`.
- Emport `xmot` via  `File->Export->Gothic 3 Motion`.

### Frame effects
When an animation is imported/exported, its frame effects are stored in/retrieved from a custom property named `frame_effects` in the corresponding action object.
The `frame_effects` custom property is a dictionary where each entry consists of a frame number (key) and an effect name (value).
It can be edited in the `Custom Properties` section of the action in Blender's Action Editor view.

## Demo
Futuristic doors in Gothic 3...

[Futuristic door example](https://github.com/georgeto/g3blend/assets/9250103/566755c9-1cc9-40cc-a89f-fd79012edbf5)

Scavenger is not convinced by this innovation!

[Scavenger not convinced](https://github.com/georgeto/g3blend/assets/9250103/0bb1a116-454b-4e1d-9cc6-bb423442dc6d)

## Credits
* Auronen
* [io_scene_fbx](https://projects.blender.org/blender/blender-addons/src/branch/main/io_scene_fbx)
* KrxImpExp
* [Kaitai Struct](https://doc.kaitai.io/)
