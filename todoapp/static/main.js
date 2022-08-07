document.getElementById("form").onsubmit = function (event) {
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

const checkboxes = document.querySelectorAll(".check-completed");
for (let i = 0; i < checkboxes.length; i++) {
  checkboxes[i].onchange = function (event) {
    const completed = event.target.checked;
    const todoId = event.target.dataset.id;
    fetch(`/todos/${todoId}/set-completed`, {
      method: "POST",
      body: JSON.stringify({
        completed: completed,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then(function (jsonResponse) {
        console.log(jsonResponse);
        document.getElementById("error").classname = "hidden";
      })
      .catch(function (error) {
        console.error(error);
        document.getElementById("error").classname = "";
      });
  };
}

const deleteBtns = document.querySelectorAll(".delete");
for (let i = 0; i < deleteBtns.length; i++) {
  deleteBtns[i].onclick = function (event) {
    event.preventDefault();
    const todoId = event.target.dataset.id;
    fetch(`/todos/${todoId}/delete`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then(function (jsonResponse) {
        console.log(jsonResponse);
        document.getElementById("error").classname = "hidden";
        const item = document.getElementById(todoId);
        item.parentElement.removeChild(item);
      })
      .catch(function (error) {
        console.error(error);
        document.getElementById("error").classname = "";
      });
  };
}
