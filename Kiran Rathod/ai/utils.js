/**
 * Construction Intelligent Hub (CIH) - AI Utility Helpers
 * 
 * Utility functions for response formatting, markdown rendering, and file downloading.
 */

const AIUtils = {
    /**
     * Download text content as a file on client machine
     */
    downloadAsFile: (filename, textContent, mimeType = "text/plain") => {
        try {
            if (!textContent) {
                alert("No report content available to download.");
                return;
            }
            const blob = new Blob([textContent], { type: `${mimeType};charset=utf-8` });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 500);
        } catch (err) {
            console.error("Failed to download file:", err);
            alert("Download failed: " + err.message);
        }
    },

    /**
     * Open report in print view to save as PDF
     */
    printAsPDF: (title, htmlContent) => {
        try {
            const printWindow = window.open('', '_blank');
            if (!printWindow) {
                alert('Please allow popups to export as PDF or print.');
                return;
            }
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>${title}</title>
                    <style>
                        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; color: #0F172A; line-height: 1.6; max-width: 900px; margin: 0 auto; }
                        h1 { color: #1D4ED8; font-size: 22px; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; margin-bottom: 16px; }
                        h2 { color: #0F172A; font-size: 16px; margin-top: 20px; margin-bottom: 8px; border-bottom: 1px solid #F1F5F9; padding-bottom: 4px; }
                        h3 { color: #334155; font-size: 14px; }
                        ul { padding-left: 20px; margin: 10px 0; }
                        li { margin-bottom: 6px; color: #334155; }
                        strong { color: #0F172A; }
                        hr { border: none; border-top: 1px solid #E2E8F0; margin: 20px 0; }
                        .header-meta { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px; margin-bottom: 24px; font-size: 13px; color: #475569; }
                        @media print { body { padding: 15px; } .no-print { display: none; } }
                    </style>
                </head>
                <body>
                    ${htmlContent}
                </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.focus();
            setTimeout(() => {
                printWindow.print();
            }, 600);
        } catch (err) {
            console.error("PDF Print failed:", err);
            alert("PDF generation failed: " + err.message);
        }
    },

    /**
     * Format markdown strings to simple clean HTML for UI display
     */
    formatMarkdownToHTML: (mdText) => {
        if (!mdText) return "";
        let text = mdText.replace(/\r\n/g, '\n');
        
        // Convert headers
        text = text.replace(/^### (.*$)/gim, '<h3 style="font-size: 15px; font-weight: 700; color: #1E293B; margin: 16px 0 6px;">$1</h3>');
        text = text.replace(/^## (.*$)/gim, '<h2 style="font-size: 17px; font-weight: 800; color: #0F172A; margin: 22px 0 8px; border-bottom: 1px solid #F1F5F9; padding-bottom: 4px;">$1</h2>');
        text = text.replace(/^# (.*$)/gim, '<h1 style="font-size: 21px; font-weight: 800; color: #1D4ED8; margin: 10px 0 14px;">$1</h1>');
        
        // Bold and italic
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #0F172A; font-weight: 700;">$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Horizontal rules
        text = text.replace(/^---$/gim, '<hr style="border: none; border-top: 1px solid #E2E8F0; margin: 18px 0;">');
        
        // List items
        text = text.replace(/^\s*[-*]\s+(.*$)/gim, '<li style="margin-bottom: 6px; color: #334155;">$1</li>');
        text = text.replace(/(<li.*<\/li>\n?)+/g, '<ul style="margin: 8px 0 14px 20px;">$&</ul>');
        
        // Paragraphs
        text = text.replace(/\n\n+/g, '</p><p style="margin-bottom: 12px; color: #334155; line-height: 1.7;">');
        text = '<p style="margin-bottom: 12px; color: #334155; line-height: 1.7;">' + text + '</p>';
        
        return text;
    },

    /**
     * Clean raw string output
     */
    cleanText: (str) => {
        if (!str) return "";
        return str.trim();
    }
};
