using UnityEngine;

namespace Mud2026.UnityPrototype
{
    public static class PrototypeBootstrap
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Boot()
        {
            if (Object.FindAnyObjectByType<WorldPrototype>() != null) return;
            new GameObject("Mud2026 Prototype").AddComponent<WorldPrototype>();
        }
    }
}
