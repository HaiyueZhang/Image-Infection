// Function to register client
document
  .getElementById("registerClient")
  .addEventListener("click", function () {
    fetch("/sendRegister", { method: "PUT" })
      .then((response) => {
        if (response.ok) {
          return response.json(); // If the response is successful, parse it as JSON
        } else {
          throw new Error("Registration failed"); // If the response is not successful, throw an error
        }
      })
      .then((data) => {
        alert("Client Registered: " + JSON.stringify(data)); // Show success message
      })
      .catch((error) => {
        alert("Error: " + error.message); // Show error message
      });
  });

// Function to upload and register image
document
  .getElementById("uploadForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    let formData = new FormData();
    formData.append("file", document.getElementById("imageInput").files[0]);

    fetch("/sendImage", {
      method: "PUT",
      body: formData,
    })
      .then((response) => {
        console.log(response); // Log the raw response
        if (response.ok) {
          if (
            response.headers.get("content-type").includes("application/json")
          ) {
            return response.json(); // Parse as JSON if the response is JSON
          } else {
            return response.text(); // Otherwise, handle it as text
          }
        } else {
          throw new Error("Image upload failed");
        }
      })
      .then((data) => {
        alert("Response: " + data); // Show the response (whether text or JSON)
      })
      .catch((error) => {
        alert("Error: " + error.message);
      });
  });

// Function to place vote
document.getElementById("placeVote").addEventListener("click", function () {
  const xloc = document.getElementById("voteXloc").value;
  const yloc = document.getElementById("voteYloc").value;
  fetch(`/castVote/${xloc}/${yloc}`, { method: "POST" })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("Failed to place vote");
      }
    })
    .then((data) => {
      alert("Vote Placed Successfully: " + JSON.stringify(data));
    })
    .catch((error) => {
      alert("Error: " + error.message);
    });
});

document.getElementById("getStatus").addEventListener("click", function () {
  fetch("/status")
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("Failed to get status");
      }
    })
    .then((statusInfo) => {
      const statusText =
        "Image Approved: " +
        statusInfo.image_approved +
        "\nTile Location - X: " +
        statusInfo.tile_location.x +
        ", Y: " +
        statusInfo.tile_location.y;
      document.getElementById("statusDisplay").innerText = statusText;
    })
    .catch((error) => {
      alert("Error: " + error.message);
    });
});

// Function to get image
document.getElementById("getImage").addEventListener("click", function () {
  fetch("/image")
    .then((response) => {
      if (response.ok) {
        return response.blob();
      } else {
        throw new Error("Failed to get image");
      }
    })
    .then((imageBlob) => {
      const imageUrl = URL.createObjectURL(imageBlob);
      document.getElementById("imageDisplay").innerHTML =
        '<img src="' + imageUrl + '" alt="Server Image"/>';
      alert("Image Retrieved Successfully");
    })
    .catch((error) => {
      alert("Error: " + error.message);
    });
});

// Function to get tile
document.getElementById("getTile").addEventListener("click", function () {
  fetch("/tile")
    .then((response) => {
      if (response.ok) {
        return response.blob();
      } else {
        throw new Error("Failed to get tile");
      }
    })
    .then((tileBlob) => {
      const tileUrl = URL.createObjectURL(tileBlob);
      document.getElementById("tileDisplay").innerHTML =
        '<img src="' + tileUrl + '" alt="Server Tile"/>';
      alert("Tile Retrieved Successfully");
    })
    .catch((error) => {
      alert("Error: " + error.message);
    });
});

document.getElementById("getVotes").addEventListener("click", function () {
  fetch("/votes")
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("Failed to get votes");
      }
    })
    .then((data) => {
      document.getElementById("votesDisplay").innerText =
        "Current Votes: " + data.votes;
    })
    .catch((error) => {
      alert("Error: " + error.message);
    });
});
