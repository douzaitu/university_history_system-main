import request from "./request";

// 知识图谱数据API
export function getKnowledgeGraphData() {
  return request({
    url: "/knowledge-graph/",
    method: "get",
  });
}

// 实体搜索API
export function searchEntities(keyword) {
  return request({
    url: "/entities/",
    method: "get",
    params: { search: keyword },
  });
}

// 获取所有实体
export function getAllEntities() {
  return request({
    url: "/entities/",
    method: "get",
  });
}

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

// 获取实体子图
export function getEntitySubgraph(id) {
  return request({
    url: `/entity-subgraph/${id}/`,
    method: "get",
  });
}

// 获取文档列表
export function getDocuments() {
  return request({
    url: "/documents/",
    method: "get",
  });
}

// 按类型获取实体
export function getEntitiesByType(type) {
  return request({
    url: "/entities/",
    method: "get",
    params: { type: type },
  });
}
