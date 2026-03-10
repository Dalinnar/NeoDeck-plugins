function open_sounds_folder(path){
    console.log("open_scenes")
    let soundboard_url = "/soundboard/scenes/";

    fetch(soundboard_url, {
        headers: {
            "X-Folder-Path": path
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.data)
        updateGrid(data.data)
    })
}