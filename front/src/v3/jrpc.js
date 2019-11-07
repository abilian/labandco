import jaysonBrowserClient from "jayson/lib/client/browser";

const callServer = function(request, callback) {
  const options = {
    method: "POST",
    body: request,
    headers: {
      "Content-Type": "application/json",
    },
  };

  // TODO: use Axios instead ?
  fetch("/rpc/", options)
    .then(function(res) {
      return res.text();
    })
    .then(function(text) {
      callback(null, text);
    })
    .catch(function(err) {
      callback(err);
    });
};

const client = jaysonBrowserClient(callServer, {
  // other options go here
});

export default client;
