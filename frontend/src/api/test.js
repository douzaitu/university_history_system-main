import { getKnowledgeGraphData, getAllEntities } from "./knowledgeGraph";

// 测试API连接
export async function testAPI() {
  try {
    console.log("测试API连接...");

    // 测试知识图谱API
    const graphData = await getKnowledgeGraphData();
    console.log("知识图谱数据:", graphData);

    // 测试实体API
    const entities = await getAllEntities();
    console.log("实体数据:", entities);

    return { success: true, graphData, entities };
  } catch (error) {
    console.error("API测试失败:", error);
    return { success: false, error };
  }
}
