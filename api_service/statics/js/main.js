// 发送消息函数
function sendMessage() {
    // 获取输入值
    const roomId = document.getElementById('room_id').value.trim();
    const message = document.getElementById('message').value.trim();
    const responseDiv = document.getElementById('response');
    
    // 验证输入
    if (!roomId) {
        responseDiv.className = 'error';
        responseDiv.textContent = '错误: 请输入群组ID';
        return;
    }
    
    if (!message) {
        responseDiv.className = 'error';
        responseDiv.textContent = '错误: 请输入消息内容';
        return;
    }
    
    // 清空响应区域并显示加载中
    responseDiv.className = '';
    responseDiv.textContent = '发送中...';
    
    // 构建请求数据 - 根据message_api.py中的MessageRequest模型
    const data = {
        room_id: roomId,
        text: message,
        at_users: "",
        message_type: "text"
    };
    
    // 获取API密钥
    const apiKey = getApiKey();
    if (!apiKey) {
        responseDiv.className = 'error';
        responseDiv.textContent = '错误: 未提供API密钥';
        return;
    }
    
    // 发送API请求 - 使用正确的API端点 /api/message/push
    fetch('/api/message/push', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + apiKey
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('API请求失败: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            responseDiv.className = 'success';
            responseDiv.textContent = '消息发送成功! 消息ID: ' + (data.data?.client_msg_id || '未知');
            // 清空消息输入框
            document.getElementById('message').value = '';
        } else {
            responseDiv.className = 'error';
            responseDiv.textContent = '错误: ' + (data.error || '发送失败');
        }
    })
    .catch(error => {
        responseDiv.className = 'error';
        responseDiv.textContent = '错误: ' + error.message;
        console.error('发送消息失败:', error);
    });
}

// 获取API密钥函数
function getApiKey() {
    // 从localStorage获取密钥
    const savedKey = localStorage.getItem('api_key');
    if (savedKey) {
        return savedKey;
    }
    
    // 如果没有保存的密钥，提示用户输入
    const key = prompt('请输入API密钥 (Bearer Token):', '');
    if (key) {
        localStorage.setItem('api_key', key);
        return key;
    }
    
    return '';
}

// 清除API密钥
function clearApiKey() {
    localStorage.removeItem('api_key');
    alert('API密钥已清除');
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 显示当前API密钥状态
    const keyStatus = document.getElementById('key-status');
    if (keyStatus) {
        const hasKey = localStorage.getItem('api_key') ? true : false;
        keyStatus.textContent = hasKey ? '已设置' : '未设置';
        keyStatus.className = hasKey ? 'status-set' : 'status-unset';
    }
});