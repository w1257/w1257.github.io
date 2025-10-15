async function loadPage(basepath,page){
    const container = document.getElementById('pageToLoad');
    const baseContainer = document.getElementById('basePagerContainer');
    baseContainer.href = "";
    if (container) {
        const response = await fetch(basepath+page);
        container.innerHTML = await response.text();;
    }
    baseContainer.href = basepath;
    scriptContainer = document.getElementById('scriptToLoad');
    if (basepath == "./pages/blogs/"){
        scriptContainer.innerHTML = "<script src='blogScript.js'></script>";
    }
    else {
        scriptContainer.innerHTML = "";
    }
}

document.addEventListener('DOMContentLoaded',() => {loadPage("./pages/","aboutMe.html")})