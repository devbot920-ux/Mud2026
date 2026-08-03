using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;

namespace Mud2026.UnityPrototype
{
    public sealed class WorldData
    {
        public JObject Root { get; }
        public IReadOnlyDictionary<int, JObject> Rooms { get; }
        public IReadOnlyDictionary<int, JObject> Npcs { get; }
        public IReadOnlyDictionary<int, JObject> Items { get; }
        public IReadOnlyDictionary<int, JObject> Spawns { get; }
        public IReadOnlyList<JObject> Edges { get; }
        public IReadOnlyList<JObject> Doors { get; }
        public IReadOnlyList<JObject> Modifiers { get; }

        private WorldData(JObject root)
        {
            Root = root;
            Rooms = Index(root, "rooms");
            Npcs = Index(root, "npcs");
            Items = Index(root, "items");
            Spawns = Index(root, "spawns");
            Edges = Objects(root, "edges");
            Doors = Objects(root, "doors");
            Modifiers = Objects(root, "modifiers");
        }

        public static WorldData ParseAndValidate(string json, bool exactPendelhavenCounts = true)
        {
            if (string.IsNullOrWhiteSpace(json)) throw new WorldValidationException("World JSON is empty.");
            JObject root;
            try { root = JObject.Parse(json); }
            catch (Exception e) { throw new WorldValidationException("World JSON is invalid: " + e.Message); }

            Require((string)root["contract"]?["name"] == "mud2026.engine-neutral-world", "Unsupported contract name.");
            Require((string)root["contract"]?["version"] == "1.0.0", "Unsupported contract version; expected 1.0.0.");
            var world = new WorldData(root);
            if (exactPendelhavenCounts)
            {
                Require(world.Rooms.Count == 63, "Expected 63 rooms.");
                Require(world.Edges.Count == 130, "Expected 130 edges.");
                Require(world.Doors.Count == 2, "Expected 2 doors.");
                Require(world.Npcs.Count == 18, "Expected 18 NPCs.");
                Require(world.Items.Count == 12, "Expected 12 items.");
                Require(world.Spawns.Count == 19, "Expected 19 spawns.");
                Require(world.Modifiers.Count == 70, "Expected 70 modifiers.");
            }
            world.ValidateReferences();
            return world;
        }

        public IEnumerable<JObject> Exits(int roomId, bool includeHidden = false) =>
            Edges.Where(e => (int)e["from_room"] == roomId && (includeHidden || !(bool)e["hidden"]));

        public int ExitCount(int roomId, bool includeHidden = false) => Exits(roomId, includeHidden).Count();
        public string FirstExitDirection(int roomId, bool includeHidden = false) => (string)Exits(roomId, includeHidden).First()["direction"];
        public int Count(string collection) => collection switch
        {
            "rooms" => Rooms.Count, "edges" => Edges.Count, "doors" => Doors.Count,
            "npcs" => Npcs.Count, "items" => Items.Count, "spawns" => Spawns.Count,
            "modifiers" => Modifiers.Count, _ => throw new ArgumentOutOfRangeException(nameof(collection))
        };
        public bool HasHiddenExit() => Edges.Any(e => (bool)e["hidden"]);
        public bool HasVerticalExit() => Edges.Any(e => (string)e["direction"] is "U" or "D");
        public bool HasParallelEdges() => Edges.GroupBy(e => ((int)e["from_room"], (string)e["direction"])).Any(g => g.Count() > 1);
        public bool HasBoundaryStubEdge() =>
            ((JArray)Root["fixture"]["stub_room_ids"]).Values<int>().Any(stub => Edges.Any(e => (int)e["from_room"] == stub || (int)e["to_room"] == stub));

        public static JToken Field(JObject entity, string name) =>
            ((JArray)entity["fields"] ?? new JArray()).OfType<JObject>().FirstOrDefault(f => (string)f["name"] == name)?["value"];

        public string RoomTitle(int id) => TextField(Rooms[id], "short_description", $"Room {id}");
        public string RoomDescription(int id) => TextField(Rooms[id], "long_description", RoomTitle(id));
        public string EntityTitle(JObject entity) => TextField(entity, "short_description", $"Entity {(int)entity["id"]}");

        private void ValidateReferences()
        {
            var edgeIds = new HashSet<int>();
            foreach (var edge in Edges)
            {
                Require(edgeIds.Add((int)edge["id"]), $"Duplicate edge id {(int)edge["id"]}.");
                Require(Rooms.ContainsKey((int)edge["from_room"]), "Edge has unknown source room.");
                Require(Rooms.ContainsKey((int)edge["to_room"]), "Edge has unknown destination room.");
                Require(DirectionVectors.All.Contains((string)edge["direction"]), "Edge has unknown direction.");
            }
            foreach (var spawn in Spawns.Values)
            {
                Require(Rooms.ContainsKey((int)spawn["id"]), "Spawn id does not identify a room.");
                foreach (var entry in ((JArray)spawn["entries"]).OfType<JObject>())
                {
                    var type = (string)entry["entity_type"];
                    var id = (int)entry["entity_id"];
                    Require(type == "npc" ? Npcs.ContainsKey(id) : type == "item" && Items.ContainsKey(id), "Spawn references unknown entity.");
                }
            }
            Require(Edges.Any(e => (int)e["from_room"] == 4057 && (int)e["to_room"] == 4058 && (string)e["direction"] == "W"), "Missing 4057 west door side.");
            Require(Edges.Any(e => (int)e["from_room"] == 4058 && (int)e["to_room"] == 4057 && (string)e["direction"] == "W"), "Missing 4058 west door side.");
        }

        private static Dictionary<int, JObject> Index(JObject root, string property)
        {
            var result = new Dictionary<int, JObject>();
            foreach (var item in Objects(root, property))
            {
                var id = (int)item["id"];
                Require(result.TryAdd(id, item), $"Duplicate {property} id {id}.");
            }
            return result;
        }

        private static List<JObject> Objects(JObject root, string property)
        {
            Require(root[property] is JArray, $"Missing {property} array.");
            return ((JArray)root[property]).OfType<JObject>().ToList();
        }

        private static string TextField(JObject entity, string name, string fallback)
        {
            var value = (string)Field(entity, name);
            return string.IsNullOrWhiteSpace(value) ? fallback : value;
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new WorldValidationException(message);
        }
    }

    public sealed class WorldValidationException : Exception
    {
        public WorldValidationException(string message) : base(message) { }
    }

    public static class DirectionVectors
    {
        public static readonly HashSet<string> All = new() { "N", "S", "E", "W", "NE", "NW", "SE", "SW", "U", "D" };
    }
}
