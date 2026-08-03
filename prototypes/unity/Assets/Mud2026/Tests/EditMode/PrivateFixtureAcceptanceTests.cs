using System.IO;
using System.Security.Cryptography;
using System;
using NUnit.Framework;
using Mud2026.UnityPrototype;

namespace Mud2026.UnityPrototype.Tests
{
    public sealed class PrivateFixtureAcceptanceTests
    {
        private const string FixturePath = @"C:\code\Mud2026\var\exports\pendelhaven-v1.json";
        private const string ExpectedSha256 = "146D19341A7172EFA604E7E32D9277A9E86750ADE26D5637CFDA1EDBBDDE2DA4";

        [Test]
        public void ExternalUnchangedPendelhavenPassesComparisonContract()
        {
            if (!File.Exists(FixturePath)) Assert.Ignore("Private fixture is not available on this machine.");
            using var stream=File.OpenRead(FixturePath);
            using var sha=SHA256.Create();
            Assert.That(BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", ""),Is.EqualTo(ExpectedSha256));
            var world=WorldData.ParseAndValidate(File.ReadAllText(FixturePath));
            Assert.That(world.Count("rooms"),Is.EqualTo(63));
            Assert.That(world.Count("edges"),Is.EqualTo(130));
            Assert.That(world.Count("doors"),Is.EqualTo(2));
            Assert.That(world.Count("npcs"),Is.EqualTo(18));
            Assert.That(world.Count("items"),Is.EqualTo(12));
            Assert.That(world.Count("spawns"),Is.EqualTo(19));
            Assert.That(world.Count("modifiers"),Is.EqualTo(70));
            Assert.That(world.HasHiddenExit(),Is.True);
            Assert.That(world.HasVerticalExit(),Is.True);
            Assert.That(world.HasBoundaryStubEdge(),Is.True);
        }
    }
}
