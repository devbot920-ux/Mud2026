using NUnit.Framework;
using Mud2026.UnityPrototype;

namespace Mud2026.UnityPrototype.Tests
{
    public sealed class WorldDataTests
    {
        private const string Synthetic = @"{
          'contract':{'name':'mud2026.engine-neutral-world','version':'1.0.0'},
          'fixture':{'primary_room_ids':[4057],'stub_room_ids':[4058]},
          'rooms':[{'id':4057,'fields':[{'name':'short_description','value':'Synthetic A'}]},{'id':4058,'fields':[{'name':'short_description','value':'Synthetic B'}]}],
          'edges':[{'id':1,'from_room':4057,'to_room':4058,'direction':'W','door':true,'hidden':false},{'id':2,'from_room':4058,'to_room':4057,'direction':'W','door':true,'hidden':false},{'id':3,'from_room':4057,'to_room':4058,'direction':'W','door':false,'hidden':true}],
          'doors':[], 'npcs':[], 'items':[], 'spawns':[], 'modifiers':[] }";

        [Test] public void ParsesSyntheticContractAndPreservesParallelEdges()
        {
            var world=WorldData.ParseAndValidate(Synthetic,false);
            Assert.That(world.ExitCount(4057,true),Is.EqualTo(2));
            Assert.That(world.FirstExitDirection(4057,false),Is.EqualTo("W"));
        }

        [Test] public void RejectsWrongVersion() => Assert.Throws<WorldValidationException>(() => WorldData.ParseAndValidate(Synthetic.Replace("1.0.0","2.0.0"),false));
        [Test] public void RejectsDanglingEdge() => Assert.Throws<WorldValidationException>(() => WorldData.ParseAndValidate(Synthetic.Replace("'to_room':4058","'to_room':9999"),false));
        [Test] public void RejectsDuplicateEdgeId() => Assert.Throws<WorldValidationException>(() => WorldData.ParseAndValidate(Synthetic.Replace("'id':2,'from_room':4058","'id':1,'from_room':4058"),false));
    }
}
