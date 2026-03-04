import request from "./request";

// 获取实体详情
export function getEntityDetail(id) {
  return request({
    url: `/entities/${id}/`,
    method: "get",
  });
}

// 获取实体关系
export function getEntityRelationships(id) {
  return request({
    url: `/entities/${id}/relationships/`,
    method: "get",
  });
}
