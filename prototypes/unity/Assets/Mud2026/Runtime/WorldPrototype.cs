using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace Mud2026.UnityPrototype
{
    public sealed class WorldPrototype : MonoBehaviour
    {
        private static readonly Dictionary<string, Vector3> Direction = new(StringComparer.OrdinalIgnoreCase)
        {
            ["N"] = Vector3.forward, ["S"] = Vector3.back, ["E"] = Vector3.right, ["W"] = Vector3.left,
            ["NE"] = new(1,0,1), ["NW"] = new(-1,0,1), ["SE"] = new(1,0,-1), ["SW"] = new(-1,0,-1),
            ["U"] = Vector3.up, ["D"] = Vector3.down
        };

        private WorldData world;
        private int roomId;
        private bool showHidden;
        private bool showDeveloper = true;
        private string command = "";
        private string status = "Loading external fixture...";
        private GameObject stage;
        private CharacterController controller;
        private Camera playerCamera;
        private float pitch;

        private void Start()
        {
            Application.runInBackground = true;
            try
            {
                var path = FixturePath();
                world = WorldData.ParseAndValidate(File.ReadAllText(path));
                roomId = world.Root["fixture"]?["primary_room_ids"]?.First?.Value<int>() ?? world.Rooms.Keys.First();
                BuildPlayer();
                EnterRoom(roomId);
                status = "Fixture validated. WASD/mouse to move; Enter opens command input.";
            }
            catch (Exception e) { status = "LOAD FAILED: " + e.Message; Debug.LogException(e); }
        }

        private static string FixturePath()
        {
            var overridePath = Environment.GetEnvironmentVariable("MUD2026_FIXTURE");
            if (!string.IsNullOrWhiteSpace(overridePath) && File.Exists(overridePath)) return overridePath;
            var candidates = new[]
            {
                Path.Combine(Application.streamingAssetsPath, "pendelhaven-v1.json"),
                Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "..", "var", "exports", "pendelhaven-v1.json")),
                @"C:\code\Mud2026\var\exports\pendelhaven-v1.json"
            };
            return candidates.FirstOrDefault(File.Exists) ?? throw new FileNotFoundException("Set MUD2026_FIXTURE to the unchanged pendelhaven-v1.json path.");
        }

        private void BuildPlayer()
        {
            var player = new GameObject("Player");
            controller = player.AddComponent<CharacterController>();
            controller.height = 1.8f; controller.radius = .35f; controller.center = new Vector3(0,.9f,0);
            playerCamera = new GameObject("Player Camera").AddComponent<Camera>();
            playerCamera.transform.SetParent(player.transform); playerCamera.transform.localPosition = new Vector3(0,1.65f,0);
            playerCamera.gameObject.AddComponent<AudioListener>();
            Cursor.lockState = CursorLockMode.Locked;
        }

        private void Update()
        {
            if (controller == null || world == null) return;
            if (Input.GetKeyDown(KeyCode.Escape)) Cursor.lockState = CursorLockMode.None;
            if (Input.GetMouseButtonDown(0) && !GUIUtility.hotControl.Equals(0)) Cursor.lockState = CursorLockMode.Locked;
            if (Cursor.lockState == CursorLockMode.Locked)
            {
                var yaw = Input.GetAxis("Mouse X") * 2f; pitch = Mathf.Clamp(pitch - Input.GetAxis("Mouse Y") * 2f, -80, 80);
                controller.transform.Rotate(0, yaw, 0); playerCamera.transform.localRotation = Quaternion.Euler(pitch,0,0);
                var move = controller.transform.TransformDirection(new Vector3(Input.GetAxisRaw("Horizontal"),0,Input.GetAxisRaw("Vertical")).normalized);
                controller.SimpleMove(move * 5f);
            }
            foreach (var portal in stage?.GetComponentsInChildren<ExitPortal>() ?? Array.Empty<ExitPortal>())
                if (Vector3.Distance(controller.transform.position, portal.transform.position) < 1.2f) Travel(portal.Edge);
        }

        private void EnterRoom(int destination)
        {
            roomId = destination;
            if (stage != null) Destroy(stage);
            stage = new GameObject("Generated Room Stage");
            MakeCube("Floor", new Vector3(0,-.25f,0), new Vector3(18,.5f,18), new Color(.16f,.18f,.21f));
            MakeCube("North wall", new Vector3(0,2.5f,9), new Vector3(18,5,.3f), Color.gray);
            MakeCube("South wall", new Vector3(0,2.5f,-9), new Vector3(18,5,.3f), Color.gray);
            MakeCube("East wall", new Vector3(9,2.5f,0), new Vector3(.3f,5,18), Color.gray);
            MakeCube("West wall", new Vector3(-9,2.5f,0), new Vector3(.3f,5,18), Color.gray);
            foreach (var edge in world.Exits(roomId, showHidden)) CreateExit(edge);
            CreateEntities();
            if (controller != null) { controller.enabled = false; controller.transform.position = new Vector3(0,.1f,0); controller.enabled = true; }
        }

        private void CreateExit(JObject edge)
        {
            var direction = (string)edge["direction"];
            var vector = Direction[direction].normalized;
            var portal = MakeCube($"Exit {direction} -> {(int)edge["to_room"]}", vector * 7.5f + Vector3.up, new Vector3(1.5f,2,.25f), (bool)edge["hidden"] ? Color.magenta : (bool)edge["door"] ? new Color(.45f,.24f,.08f) : Color.cyan);
            portal.transform.LookAt(Vector3.zero + Vector3.up);
            portal.AddComponent<ExitPortal>().Edge = edge;
        }

        private void CreateEntities()
        {
            if (!world.Spawns.TryGetValue(roomId, out var spawn)) return;
            var entries = ((JArray)spawn["entries"]).OfType<JObject>().ToArray();
            for (var i=0; i<entries.Length; i++)
            {
                var e=entries[i]; var type=(string)e["entity_type"]; var id=(int)e["entity_id"];
                var source = type == "npc" ? world.Npcs[id] : world.Items[id];
                var marker=MakeCube(world.EntityTitle(source), new Vector3(-3+i*2, type=="npc" ? 1 : .35f, 2), type=="npc" ? new Vector3(.8f,2,.8f) : Vector3.one*.6f, type=="npc" ? Color.red : Color.yellow);
                marker.name += $" x{(int)e["count"]}";
            }
        }

        private GameObject MakeCube(string name, Vector3 position, Vector3 scale, Color color)
        {
            var go=GameObject.CreatePrimitive(PrimitiveType.Cube); go.name=name; go.transform.SetParent(stage.transform); go.transform.position=position; go.transform.localScale=scale;
            var material=new Material(Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard")); material.color=color; go.GetComponent<Renderer>().material=material; return go;
        }

        private void Travel(JObject edge) { EnterRoom((int)edge["to_room"]); status=$"Traversed edge {(int)edge["id"]}."; }

        private void ExecuteCommand()
        {
            var raw=command.Trim().ToLowerInvariant(); command="";
            if (raw == "look") { status=world.RoomDescription(roomId); return; }
            var aliases=new Dictionary<string,string>{{"n","N"},{"s","S"},{"e","E"},{"w","W"},{"ne","NE"},{"nw","NW"},{"se","SE"},{"sw","SW"},{"u","U"},{"d","D"}};
            if (!aliases.TryGetValue(raw,out var direction)) { status="Commands: n s e w ne nw se sw u d look"; return; }
            var matches=world.Exits(roomId,showHidden).Where(e=>(string)e["direction"]==direction).ToArray();
            if (matches.Length==0) status=$"No visible exit {direction}."; else { if(matches.Length>1) status=$"Parallel exit: selecting edge {(int)matches[0]["id"]} of {matches.Length}."; Travel(matches[0]); }
        }

        private void OnGUI()
        {
            var width=Mathf.Min(620,Screen.width-20); GUILayout.BeginArea(new Rect(10,10,width,Screen.height-20),GUI.skin.box);
            GUILayout.Label(world == null ? "Mud2026 Unity Prototype" : $"{world.RoomTitle(roomId)}  [room {roomId}]");
            if(world!=null){ GUILayout.Label(world.RoomDescription(roomId)); GUILayout.Label("Exits: "+string.Join(", ",world.Exits(roomId,showHidden).Select(e=>$"{e["direction"]}->{e["to_room"]}#{e["id"]}"))); }
            GUILayout.Label(status);
            GUILayout.BeginHorizontal(); GUILayout.Label(">",GUILayout.Width(15)); command=GUILayout.TextField(command); if(GUILayout.Button("Run",GUILayout.Width(50))) ExecuteCommand(); GUILayout.EndHorizontal();
            if(Event.current.isKey && Event.current.keyCode==KeyCode.Return){ ExecuteCommand(); Event.current.Use(); }
            var oldHidden=showHidden; showHidden=GUILayout.Toggle(showHidden,"Show hidden exits"); if(oldHidden!=showHidden && world!=null) EnterRoom(roomId);
            showDeveloper=GUILayout.Toggle(showDeveloper,"Developer overlay");
            if(showDeveloper && world!=null) GUILayout.Label($"contract 1.0.0 | rooms {world.Rooms.Count} | edges {world.Edges.Count} | provenance retained | hidden {(showHidden?"shown":"filtered")}");
            GUILayout.EndArea();
        }
    }

    public sealed class ExitPortal : MonoBehaviour { [NonSerialized] public JObject Edge; }
}
