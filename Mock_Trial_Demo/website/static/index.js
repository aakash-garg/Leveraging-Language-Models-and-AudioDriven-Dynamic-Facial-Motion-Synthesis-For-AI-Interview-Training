function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/history";
  });
}

function editChat(chatId) {
  fetch("/edit-chat", {
    method: "POST",
    body: JSON.stringify({ chatId: chatId }),
  })
}
let recognition = null;
let isSpaceKeyDown = false;
let isRecognitionRunning = false;

function speechToText(inputField) {
  if (isRecognitionRunning) {
    return;
  }

  recognition = new webkitSpeechRecognition();
  recognition.lang = "en-US";

  recognition.onresult = function (event) {
    if (event.results && event.results[0]) {
      var transcript = event.results[0][0].transcript;
      const textInput = document.querySelector('input[type="text"]');
      textInput.value = transcript;
    } else {
      console.log('No speech was recognized');
    }
  };

  recognition.onerror = function (event) {
    console.log('Error occurred in recognition: ' + event.error);
  };

  recognition.onend = function (event) {
    isRecognitionRunning = false;
    recognition = null;
    if (!isSpaceKeyDown && event.results && event.results[0]) {
      const transcript = event.results[0][0].transcript;
      document.querySelector('input').value = transcript;
    }
  };
  

  recognition.start();
  isRecognitionRunning = true;
  return recognition;
}

function stopSpeechToText() {
  if (recognition) {
    recognition.onend = null;
    recognition.stop();
    recognition = null;
    isRecognitionRunning = false;
  }
}

document.addEventListener("keydown", function (event) {
  if (event.key === " ") {
    isSpaceKeyDown = true;
    if (!isRecognitionRunning) {
      recognition = speechToText(document.querySelector('input'));
    }
  }
});

document.addEventListener("keyup", function (event) {
  if (event.key === " ") {
    isSpaceKeyDown = false;
    stopSpeechToText();
  }
});

function textToSpeech(message, updateHtmlCallback) {
  return new Promise((resolve, reject) => {
      fetch('./text-to-speech', {
          method: 'POST',
          body: JSON.stringify({ text: message }),
          headers: {
              'Content-Type': 'application/json'
          },
      })
      .then(response => response.json())
      .then(data => {
          const placeholder = document.querySelector('#placeholder');

          const handleVideoEnd = () => {
              fetch('/delete-video/' + data.filename, {
                  method: 'POST',
              });
              resolve(); // Resolve the promise when the video ends
          };

          if (placeholder.tagName === 'IMG') {
              const video = document.createElement('video');
              video.id = 'placeholder';
              video.src = "/static/" + data.filename + "?t=" + new Date().getTime();
              video.autoplay = true;
              video.addEventListener('ended', handleVideoEnd);
              placeholder.parentNode.replaceChild(video, placeholder);
              updateHtmlCallback();
          } else {
              placeholder.src = "/static/" + data.filename + "?t=" + new Date().getTime();
              placeholder.load();
              updateHtmlCallback();
              placeholder.play();
              placeholder.addEventListener('ended', handleVideoEnd);
          }
      })
      .catch(error => {
          reject(error); // Reject the promise in case of an error
      });
  });
}

class Chatbox {
  constructor() {
    this.args = {
      // openButton: document.querySelector('.chatbox__button'),
      chatBox: document.querySelector('.chatbox__support'),
      sendButton: document.querySelector('.send__button'),
      resetButton: document.querySelector('.reset__button'),
      editButton: document.querySelector('.edit__button'),

    }

    this.state = true;
    this.messages = [];
    this.voiceInteraction = false;
  }

  display() {
    const { chatBox, chatBox_footer, sendButton, editButton,  resetButton } = this.args;

    // Add event listener for the checkbox
    const voiceInteractionCheckbox = document.querySelector("#voiceInteraction");
    voiceInteractionCheckbox.addEventListener('change', (event) => {
      this.voiceInteraction = event.target.checked;
    });
  
    // Change the event listener for the input field
    const node = chatBox.querySelector('input');
    const imageButton = document.querySelector('.image-button'); // Image button
    let recognition;
  
    const handleKeyDown = (event) => {
      if (event.key === "Enter") {
        if (this.voiceInteraction && (event.target === node || event.target === document.body)) {
          event.preventDefault(); // Prevent the default form submission behavior
        }
        this.onSendButton(chatBox);
      }
    };
  
    const handleSpaceKey = (event) => {
      if (this.voiceInteraction) {
        event.preventDefault();
        recognition = speechToText(node);
      }
    };
    
    document.addEventListener("keydown", handleKeyDown);
  
    node.addEventListener("keydown", (event) => {
      if (event.key === " ") {
        handleSpaceKey(event);
      }
    });
  
    node.addEventListener("keyup", (event) => {
      if (this.voiceInteraction && event.key === " ") {
        if (!isSpaceKeyDown) {
          stopSpeechToText();
        }
      }
    });
  
    // Add event listener to the image button
    imageButton.addEventListener('click', handleSpaceKey);
    sendButton.addEventListener('click', () => this.onSendButton(chatBox));
    resetButton.addEventListener('click', () => this.onResetButton(chatBox));
  } 
    // openButton.addEventListener('click', () => this.toggleState(chatBox))

  //   sendButton.addEventListener('click', () => this.onSendButton(chatBox))
  //   resetButton.addEventListener('click', () => this.onResetButton(chatBox))

  //   // editButton.addEventListener('click', () => this.oneditButton(chatBox))

  //   const node = chatBox.querySelector('input');
  //   node.addEventListener("keyup", ({ key }) => {
  //     if (key === "Enter") {
  //       this.onSendButton(chatBox)
  //     }
  //   })
  // }
  onSendButton(chatbox) {
    var textField = chatbox.querySelector('input[type="text"]');
    let text1 = textField.value
    if (text1 === "") {
        return;
    }

    let msg1 = { name: "User", message: text1 }
    this.messages.push(msg1);
    textField.value = ''


    // Add "Pastor is typing..." message before sending the request
    let typingMessage = { name: "Sam", message: "Prosecutor is typing...", isTyping: true, class: "blink" };
    this.messages.push(typingMessage);
    this.updateChatText(chatbox)

    // // Add "Pastor is typing..." message or loading spinner here
    // let typingMessage = document.createElement("div");
    // typingMessage.classList.add("messages__item", "messages__item--visitor", "typing");
    // typingMessage.innerHTML = "Pastor is typing...";
    // chatbox.querySelector('.chatbox__messages').appendChild(typingMessage);

    fetch('./predict', {
        method: 'POST',
        body: JSON.stringify({ message: text1 }),
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(r => r.json())
        .then(r => {
            let msg2 = { name: "Sam", message: r.answer, parsed_message: r.parsed_answer, id: r.id};
            console.log(msg2)
            // Remove "Pastor is typing..." message or loading spinner here
            this.messages.pop();
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            

      }).catch((error) => {
        console.error('Error:', error);
        this.updateChatText(chatbox)
        textField.value = ''
      });
    }



  updateChatHTML(html) {
    const chatmessage = this.args.chatBox.querySelector('.chatbox__messages');
    chatmessage.innerHTML = html;
  }

  async updateChatText(chatbox) {
    var html = '';
    this.messages.slice().reverse().forEach(function (item, index) {
      if (item.isTyping) {
        html += '<div class="messages__item messages__item--visitor ' + item.class + '">' + item.message + '</div>'
    }

      if (item.name === "Sam" && !item.isTyping) {
        html += '<form action="/" method="POST"><div class="messages__item messages__item--visitor">' + item.message + '</br><a class="uil uil-pen edit__button" href="/update/' + item.id + '" target="_blank" rel="noopener noreferrer"> Edit</a></div></form>'
        
      }
      else if (!item.isTyping){
        html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
      }
    });
    if (this.voiceInteraction) {
      console.log("inside voice ineraction");
      let lastMessage = this.messages[this.messages.length - 1];
      if (lastMessage && lastMessage.name === "Sam" && !lastMessage.isTyping) {
        console.log(lastMessage.message);
        try{
          await textToSpeech(lastMessage.message, this.updateChatHTML.bind(this, html));
        }
        catch(error){
          console.log("Text too big!")
        }
      }
    }

    const chatmessage = chatbox.querySelector('.chatbox__messages');
    chatmessage.innerHTML = html;
  }
  onResetButton(chatbox) {
    var textField = chatbox.querySelector('input');
    let text1 = '<reset>'

    let msg1 = { name: "User", message: text1 }
    this.messages.push(msg1);
    textField.value = ''

    let typingMessage = { name: "Allen", message: "Resetting...", isTyping: true, class: "blink" };
    this.messages.push(typingMessage);
    this.updateChatText(chatbox)

    fetch('./predict', {
        method: 'POST',
        body: JSON.stringify({ message: text1 }),
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(r => r.json())
        .then(r => {
            let msg2 = { name: "Sam", message: r.answer, id: r.id };
            this.messages.pop();
            this.messages.push(msg2);
            this.updateChatText(chatbox)
        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
        });
  }
}


const chatbox = new Chatbox();
chatbox.display();
// chatbox.edit();
