import { app } from "/scripts/app.js";

app.registerExtension({
    name: "GntsAssetsManager",
    commands: [
        {
            id: "open-gnts",
            label: "Gnt's Assets Manager",
            function: () => {
                window.open("/gnts-assets-manager", "_blank");
            }
        }
    ],
    menuCommands: [
        {
            path: [],          // 可多级，如 ["Extensions", "My Tools"]
            commands: ["open-gnts"]
        }
    ]
});