const downloadButton = document.getElementById('download-button');
const messageDiv = document.getElementById('message');
const fileListBody = document.getElementById('file-list-body');
const urlInput = document.getElementById('url');
const urlHelp = document.getElementById('url-help');

function validateUrl(url) {
    const bvPattern = /^BV[a-zA-Z0-9]{10}$/;
    const urlPattern = /^https?:\/\/(www\.)?bilibili\.com\/video\/.+/;
    return bvPattern.test(url) || urlPattern.test(url);
}

urlInput.addEventListener('blur', () => {
    if (!urlInput.value) {
        urlHelp.textContent = '';
        urlHelp.classList.remove('show');
    } else if (!validateUrl(urlInput.value)) {
        urlHelp.textContent = '请输入有效的 Bilibili 视频 URL 或 BV 号';
        urlHelp.classList.add('show');
    } else {
        urlHelp.textContent = '';
        urlHelp.classList.remove('show');
    }
});
function toggleDownloadButton() {
    downloadButton.disabled = !validateUrl(urlInput.value);
}
urlInput.addEventListener('input', () => {
    toggleDownloadButton();
    if (!urlInput.value) {
        urlHelp.textContent = '';
        urlHelp.classList.remove('show');
    } else if (!validateUrl(urlInput.value)) {
        urlHelp.textContent = '请输入有效的 Bilibili 视频 URL 或 BV 号';
        urlHelp.classList.add('show');
    } else {
        urlHelp.textContent = '';
        urlHelp.classList.remove('show');
    }
});

// 添加 Enter 键支持
urlInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !downloadButton.disabled) {
        // event.preventDefault(); // 防止表单默认提交行为（如果有表单）
        downloadButton.click(); // 触发下载按钮的点击事件
    }
});

// 初始化按钮状态
toggleDownloadButton();

// 下载按钮点击事件
downloadButton.addEventListener('click', () => {
    if (!validateUrl(urlInput.value)) {
        messageDiv.textContent = '请输入有效的 Bilibili 视频 URL 或 BV 号';
        messageDiv.className = 'error';
        return;
    }
    const url = document.getElementById('url').value;
    const type = document.getElementById('type').value;
    const mp3Conversion = document.getElementById('mp3_conversion').checked;

    messageDiv.textContent = '下载中...';
    messageDiv.className = '';
    downloadButton.disabled = true; // 禁用按钮
    downloadButton.textContent = '下载中...'; // 更改按钮文本

    fetch('/downloads/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken() // 添加CSRF令牌
        },
        body: JSON.stringify({ url, type, mp3_conversion: mp3Conversion })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                messageDiv.textContent = `${data.message} 标题: ${data.title}`;
                messageDiv.className = 'success';
                updateFileList(); // 下载成功后更新文件列表
            } else {
                messageDiv.textContent = data.message;
                messageDiv.className = 'error';
            }
        })
        .catch(error => {
            messageDiv.textContent = `发生错误: ${error}`;
            messageDiv.className = 'error';
        })
        .finally(() => {
            downloadButton.disabled = false; // 恢复按钮
            downloadButton.textContent = '下载'; // 恢复按钮文本
        });
});

// 获取CSRF令牌
function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// 更新文件列表
function updateFileList() {
    fileListBody.innerHTML = '<tr><td colspan="5">加载中...</td></tr>'; // 修改 colspan 为 5
    fetch('/files/').then(response => response.json()).then(data => {
        fileListBody.innerHTML = ''; // 清空现有列表
        if (data.files && data.files.length > 0) {
            data.files.forEach(file => {
                const row = document.createElement('tr');
                // 对文件名进行编码，确保特殊字符被正确处理
                const encodedFilename = encodeURIComponent(file.name);
                row.innerHTML = `
                         <td>${file.name}</td>
                         <td>${file.size_formatted}</td>
                         <td>${file.created_date}</td>
                         <td>${file.modified_date}</td>
                         <td><a href="/download/${encodedFilename}/" download="${file.name}" aria-label="下载文件 ${file.name}">下载</a></td>
                      `;
                fileListBody.appendChild(row);
            });
        } else {
            fileListBody.innerHTML = '<tr><td colspan="5">没有已下载的文件</td></tr>';
        }
    })
        .catch(error => {
            console.error('获取文件列表失败:', error);
            fileListBody.innerHTML = '<tr><td colspan="5">获取文件列表失败</td></tr>';
        });
}
// 页面加载时更新文件列表