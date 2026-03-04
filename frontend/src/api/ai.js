import request from "./request";

// AI问答
export function askAI(question) {
  return request({
    url: "/ai/ask/",
    method: "post",
    data: {
      question: question,
    },
  });
}
