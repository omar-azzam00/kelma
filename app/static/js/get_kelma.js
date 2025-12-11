async function getKelma(id, username){
    let url = new URL(window.location);
    url.pathname = "api/kelma";
    
    if(id !== undefined){
        url.searchParams.set('id', id);
    }  
    if (username !== undefined){
        url.searchParams.set('username', username);
    }

    resp = await fetch(url);
    console.log(resp);
    json = await resp.json();
    console.log(json);

    return json;
}