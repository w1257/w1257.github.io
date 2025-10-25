
const blogTemplate = '\
    <div style="border-bottom: solid #555; padding: 4mm;position: relative;">\
    <p style="color: #777; left: 4mm; font-size: small;">{8} #{7}</p>\
        <h1>{0}</h1>\
        <h2>Situation</h2>\
        {1}\
        <h2>Task</h2>\
        {2}\
        <h2>Action</h2>\
        {3}\
        <h2>Result</h2>\
        {4}\
        <div>{5}</div>\
        <p style="text-align: right; color: #777; right: 4mm; font-size: small;">{6}</p>\
    </div>'

function format(str, ...values) {
  return str.replace(/{(\d+)}/g, function(match, index) {
    return typeof values[index] !== 'undefined' ? values[index] : match;
  });
}

async function blogLoad() {
    const nameContainer = document.getElementById('BlogName');
    const blogContainer = document.getElementById('BlogContent');

    const address = "./jsons/"+nameContainer.innerHTML.replaceAll(" ","-")+".json";

    blogContainer.innerHTML = address;
    const response = await fetch(address);
    const blogData = await response.json();

    //blogContainer.innerHTML = blogData["posts"][0]["Title"];
    //return;
    
    blogContainer.innerHTML = "";
    for (let i = 0; i < blogData["posts"].length ; i++) {
        //const element = array[index];
        //blogContainer.innerHTML = blogData["posts"][i]["Title"];
        let localTime = new Date(blogData["posts"][i]["Time"]);
        blogContainer.innerHTML = blogContainer.innerHTML + format(blogTemplate,blogData["posts"][i]["Title"],blogData["posts"][i]["Situation"],blogData["posts"][i]["Task"],blogData["posts"][i]["Action"],blogData["posts"][i]["Result"],blogData["posts"][i]["Extra"],localTime.toString(),blogData["posts"].length-i,nameContainer.innerHTML);
    }

}

