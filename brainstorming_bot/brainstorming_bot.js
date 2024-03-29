// UID:
// 6zqJqnT3WKRBoZiUlQgoByT_-Yw-xpK1z9qY5bp7Kjo

// Secret:
// a6rh5fjSGaaMzP5GnMcrTZB-sKbm_eSY2Tpe6PrLhB8

// Callback urls:
// https://www.are.na/hongfei-ji/

const Arena = require("are.na");

const arena = new Arena({ accessToken: "Dw8Ik4PDPKsW6cyPenhXjYGJA0Fqb89-zStZxPOAymA" });

// arena
//   .channel("brainstorming_proto3")
//   .get()
//   .then(chan => {
//     chan.contents.map(item => {
//       console.log(item.title);
//     });
//   })
//   .catch(err => console.log(err));

arena.channel('brainstorming_proto3').createBlock({
    content: "API",
    source: "https://github.com/ivangreene/arena-js"
  }).then(response => {
    console.log(response); // Log the response to see the added block
  }).catch(err => {
    console.error(err); // Log any errors
  });