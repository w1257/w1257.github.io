async function loadPage(basepath,page){
    const container = document.getElementById('pageToLoad');
    const baseContainer = document.getElementById('basePagerContainer');
    baseContainer.href = basepath;
    if (container) {
        const response = await fetch(page);
        container.innerHTML = await response.text();;
    }
}

document.addEventListener('DOMContentLoaded',() => {loadPage("./pages/","./aboutMe.html")})