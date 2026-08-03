using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build;
using UnityEngine;

namespace Mud2026.UnityPrototype.Editor
{
    public static class BuildPrototype
    {
        [MenuItem("Mud2026/Build Windows Prototype")]
        public static void BuildWindows()
        {
            Directory.CreateDirectory("Assets/Scenes");
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            EditorSceneManager.SaveScene(scene,"Assets/Scenes/Prototype.unity");
            var options=new BuildPlayerOptions { scenes=new[]{"Assets/Scenes/Prototype.unity"}, locationPathName="Builds/Windows/Mud2026Unity.exe", target=BuildTarget.StandaloneWindows64, options=BuildOptions.Development };
            var report=BuildPipeline.BuildPlayer(options);
            if(report.summary.result!=UnityEditor.Build.Reporting.BuildResult.Succeeded) throw new BuildFailedException(report.summary.result.ToString());
        }
    }
}
