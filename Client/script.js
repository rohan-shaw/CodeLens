// // Get all nav links
// const navLinks = document.querySelectorAll('.nav-link');

// // Add a click event listener to each link
// navLinks.forEach(link => {
//   link.addEventListener('click', () => {
//     // Remove the 'active' class from all links
//     navLinks.forEach(link => link.classList.remove('active'));

//     // Add the 'active' class to the clicked link
//     link.classList.add('active');
//   });
// });

// // Initially set the active link based on the current page URL
// const currentPageUrl = window.location.href;
// navLinks.forEach(link => {
//   if (link.href === currentPageUrl) {
//     link.classList.add('active');
//   }
// });

const scrollDownBtn = document.querySelector(".arrow");

const sameCodeThreshold = 70;

// user input codes
const userOriginalCodeTextArea = document.querySelector("#userOriginalCode");
const userModifiedCodeTextArea = document.querySelector("#userNewCode");

const orgCodeLines = document.querySelectorAll(".org-lines");
const orgCodeChars = document.querySelectorAll(".org-chars");
const userReqLeft = document.querySelectorAll(".requests-remaining");

const startCompareBtn = document.querySelector("#startCodeCompare-btn");

let similarityRatio = document.querySelector("#sr-boxres");
let isSameCode = document.querySelector("#sc-boxres");

let diff2htmlCodeBlock = document.querySelector("#diff-org");

// server compaire results
const responseOriginalCode = document.querySelector("#responseOriginalCode");
const responseModifiedCode = document.querySelector("#responseNewCode");
const responseCodeLines = document.querySelectorAll(".new-lines");
const responseCodeChars = document.querySelectorAll(".new-chars");

const shareBtn = document.querySelector("#shareBtn");
const copyLinkBtn = document.querySelector("#copyLinkBtn");
const sharedLink = "https://codelens.onrender.com";
const loaderGif = document.querySelector("#loadergif");

document
  .querySelectorAll(".lines")
  .forEach((line) => console.log(line.innerText));

userOriginalCodeTextArea.placeholder =
  'function example() {\n    return "original code";\n}';
userModifiedCodeTextArea.placeholder =
  'function example() {\n    return "my modified code";\n}';

function compareCode() {
  const userOriginalCode = userOriginalCodeTextArea.value
    ? userOriginalCodeTextArea.value
    : userOriginalCodeTextArea.placeholder;
  const userModifiedCode = userModifiedCodeTextArea.value
    ? userModifiedCodeTextArea.value
    : userModifiedCodeTextArea.placeholder;

  var apiUrl = `https://codelens.onrender.com/compare?code1=${userOriginalCode}&code2=${userModifiedCode}`;

  var xhr = new XMLHttpRequest();

  // Configure the GET request
  xhr.open("POST", apiUrl, true);

  xhr.setRequestHeader("Access-Control-Expose-Headers", "*");
  xhr.setRequestHeader("Access-Control-Allow-Origin", "*");
  xhr.setRequestHeader("Access-Control-Allow-Credentials", "true");
  xhr.setRequestHeader("accept", "application/json");

  // Set up a callback function to handle the response
  xhr.onreadystatechange = function () {
    // Check if the request is complete
    if (xhr.readyState == 4) {
      // Check if the request was successful (status code 200)
      if (xhr.status == 200) {
        // const rateLimitHeaders = xhr.getResponseHeader("X-RateLimit-Limit");
        console.log(rateLimitHeaders);
        // Parse the JSON response, if applicable
        var jsonResponse = JSON.parse(xhr.responseText);

        //get ratelimit headers

        console.log(jsonResponse);
        document.querySelector(".home-three").style.display = "block";
        document.querySelector(".home-three").scrollIntoView();
        isSameCode.innerText =
          jsonResponse.similarity_percentage >= sameCodeThreshold
            ? "Yes"
            : "No";
        similarityRatio.innerText = parseFloat(
          jsonResponse.similarity_percentage
        ).toFixed(2);

        updateDiff(userOriginalCode, userModifiedCode);

        // responseOriginalCode.innerText = jsonResponse.diff_result;
        // responseModifiedCode.innerText = jsonResponse.diff_result;
        // Do something with the jsonResponse
      } else {
        // Handle errors here
        console.error("Error: " + xhr.status);
      }
    }
  };

  // Send the request
  xhr.send();
}

function updateDiff(userOriginalCode, userModifiedCode) {
  let mydiff = Diff.createPatch(
    "",
    userOriginalCode,
    userModifiedCode,
    "original_code",
    "modified_code"
  );
  diff2htmlCodeBlock.value = mydiff;
  diff2html(mydiff);
  console.log(mydiff);
}

function diff2html(mydiff) {
  let config = {
    drawFileList: true,
    fileListToggle: false,
    fileListStartVisible: false,
    fileContentToggle: false,
    matching: "lines",
    outputFormat: "side-by-side",
    synchronisedScroll: true,
    highlight: true,
    renderNothingWhenEmpty: false,
  };
  diff2HTML = new Diff2HtmlUI(diff2htmlCodeBlock, mydiff, config);
  diff2HTML.draw();
  diff2HTML.highlightCode();
}

function shareCode() {
  loaderGif.style.display = "block";
  const data = `title=default&description=default&code1=${userOriginalCodeTextArea.value}&code2=${userModifiedCodeTextArea.value}`;

  let xhr = new XMLHttpRequest();
  xhr.withCredentials = true;
  xhr.open("POST", "https://codelens.onrender.com/save/{pair_id}");
  xhr.setRequestHeader("Access-Control-Allow-Origin", "*");
  xhr.setRequestHeader("Access-Control-Allow-Credentials", "true");
  xhr.setRequestHeader("accept", "application/json");

  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

  xhr.onload = function () {
    console.log(xhr.response);
    loaderGif.style.display = "none";
    if (xhr.status == 200) {
      sharedLink = xhr.response.id;
      console.log(sharedLink);
      copylink();
    }
  };

  xhr.send(data);
}

function copylink() {
  navigator.clipboard.writeText(sharedLink);
  copyLinkBtn.innerText = "Copied!";
  setTimeout(() => {
    copyLinkBtn.innerText = "Copy Link";
  }, 2000);
}

function getLinesAndChars(textareaId) {
  const textarea = document.getElementById(textareaId);

  if (!textarea) {
    console.error("Textarea with the provided ID not found.");
    return null;
  }

  const content = textarea.value;
  const lines = content.split("\n");
  const numberOfLines = lines.length;
  const numberOfChars = content.length;

  return {
    lines: numberOfLines,
    chars: numberOfChars,
  };
}

startCompareBtn.addEventListener("click", compareCode);

// shareBtn.addEventListener("click", shareCode);

// copyLinkBtn.addEventListener("click", copylink);

scrollDownBtn.addEventListener("click", () => {
  document.querySelector(".home-two").scrollIntoView();
});

userOriginalCodeTextArea.addEventListener("input", () => {
  const { lines, chars } = getLinesAndChars("userOriginalCode");
  document.querySelector(".org-lines").innerText = lines;
  document.querySelector(".org-chars").innerText = chars;
});

userModifiedCodeTextArea.addEventListener("input", () => {
  const { lines, chars } = getLinesAndChars("userNewCode");
  document.querySelector(".new-lines").innerText = lines;
  document.querySelector(".new-chars").innerText = chars;
});

// Adding highlight.js
startCompareBtn.addEventListener('click', ()=>{
  document.querySelectorAll('textarea').forEach((el)=>{
    hljs.highlightElement(el);
  })
})