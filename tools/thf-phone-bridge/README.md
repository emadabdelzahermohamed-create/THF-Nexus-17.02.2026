# THF Phone Bridge

Temporary, owner-authorized Android accessibility bridge used only for physical QA of THF apps on the user's own device.

Security scope:
- Commands require an explicit token.
- The bridge is intended to be enabled only during QA and removed afterward.
- No network listener is opened.
- Commands arrive through an explicit Android broadcast and results are emitted to a dedicated logcat tag.
- The bridge does not bypass the device lock or authentication.
