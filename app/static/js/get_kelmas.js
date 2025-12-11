async function getKelmas(start = 0, size = 20, page = 0) {
    let url = new URL(window.location);
    url.pathname = "api/kelmas";
    url.searchParams.append("start", start);
    url.searchParams.append("page", page);
    url.searchParams.append("size", size);
    // console.log(url);

    let resp = await fetch(url);
    let data = await resp.json();

    // console.log(data);
    return data;
}