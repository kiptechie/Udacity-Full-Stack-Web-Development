document.getElementById("form").onsubmit = async function (event) {
  event.preventDefault();
  fetch("/todos/create", {
    method: "POST",
    body: JSON.stringify({
      description: document.getElementById("description").value,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (jsonResponse) {
      console.log(jsonResponse);
      const liItem = document.createElement("LI");
      liItem.innerHTML = jsonResponse["description"];
      document.getElementById("todos").appendChild(liItem);
      document.getElementById("error").classname = "hidden";
      document.getElementById("description").value = "";
    })
    .catch(function (error) {
      console.error(error);
      document.getElementById("error").classname = "";
    });
};
