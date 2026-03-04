// 默认人物数据（初始为空，将从JSON文件加载）
export const people = [];

// 生成唯一ID的辅助函数
function generateUniqueId(name, index) {
  return `${name.toLowerCase().replace(/\s+/g, '-')}-${index}`;
}

// 处理图片路径的辅助函数
function processImagePath(path) {
  // 移除public前缀，因为public文件夹在Vite中会被映射到根路径
  return path.replace('public', '');
}

// 加载人物数据的函数，从public/People/导师信息汇总.json加载
export const loadPeopleData = async () => {
  try {
    // 从public文件夹加载JSON文件
    const response = await fetch('/People/导师信息汇总.json');
    if (!response.ok) {
      throw new Error(`加载导师信息失败: HTTP ${response.status}`);
    }
    
    // 获取JSON数据
    const jsonData = await response.json();
    
    // 确保数据是数组格式
    if (!Array.isArray(jsonData)) {
      console.error('JSON数据格式不正确，应为数组');
      return [];
    }
    
    // 转换数据格式，适配中文JSON字段
    const processedData = jsonData.map((person, index) => {
      // 合并简介内容
      let bio = person.简介 || '';
      if (person.详细内容 && person.详细内容 !== bio) {
        bio += ' ' + person.详细内容;
      }
      bio = bio.trim() || '暂无简介';
      
      // 确定类别（默认为教授）
      let category = '教授';
      const name = person.姓名 || '未知姓名';
      
      // 如果简介中包含其他职称，尝试提取
      if (bio.includes('副教授')) {
        category = '副教授';
      } else if (bio.includes('讲师')) {
        category = '讲师';
      }
      
      return {
        id: generateUniqueId(name, index),
        name: name,
        category: category,
        readCount: Math.floor(Math.random() * 500) + 100, // 随机阅读量
        photo: person.图片 ? processImagePath(person.图片) : '/People/default.jpg',
        bio: bio
      };
    });
    
    console.log('成功加载并处理了', processedData.length, '位导师信息');
    return processedData;
  } catch (error) {
    console.error('加载导师信息时出错:', error);
    return [];
  }
};

// 预加载图片的函数
export const preloadImages = (peopleList) => {
  if (!Array.isArray(peopleList)) return;
  
  peopleList.forEach(person => {
    if (person.photo) {
      const img = new Image();
      img.src = person.photo;
      // 图片加载失败时使用默认图片
      img.onerror = () => {
        person.photo = '/People/default.jpg';
      };
    }
  });
};