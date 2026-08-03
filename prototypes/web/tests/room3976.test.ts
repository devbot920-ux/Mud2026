import { describe, expect, it } from "vitest";
import { constrainInitialRoomMovement, findInitialRoomTarget, initialRoomCommand } from "../src/room3976";

describe("room 3976 movement", () => {
  it("allows ordinary movement within the chamber", () => expect(constrainInitialRoomMovement({x:2,z:-3})).toEqual({x:2,z:-3}));
  it("blocks movement through each outer wall", () => {
    expect(constrainInitialRoomMovement({x:20,z:-20})).toEqual({x:8.45,z:-8.45});
    expect(constrainInitialRoomMovement({x:-20,z:20})).toEqual({x:-8.45,z:8.45});
  });
});

describe("room 3976 interaction targeting", () => {
  it("targets the old man when nearby and facing him", () => expect(findInitialRoomTarget({x:2.7,z:-4.5},{x:0,z:-1})).toBe("old-man"));
  it("targets the parchment when nearby and facing it", () => expect(findInitialRoomTarget({x:-2.6,z:-6},{x:0,z:-1})).toBe("parchment"));
  it("does not interact through distance or behind the player", () => {
    expect(findInitialRoomTarget({x:0,z:0},{x:0,z:-1})).toBeUndefined();
    expect(findInitialRoomTarget({x:2.7,z:-6},{x:0,z:1})).toBeUndefined();
  });
});

describe("room 3976 text commands", () => {
  it.each([
    ["look", "look-room"],
    ["examine old man", "inspect-old-man"],
    ["talk to the old man", "talk-old-man"],
    ["read parchment", "read-parchment"],
    ["look at the old parchment", "read-parchment"],
    ["take parchment", "take-parchment"],
  ])("maps %s to %s", (command, action) => expect(initialRoomCommand(command)).toBe(action));
  it("leaves unrelated and movement commands to the world command handler", () => {
    expect(initialRoomCommand("west")).toBeUndefined();
    expect(initialRoomCommand("dance")).toBeUndefined();
  });
});
