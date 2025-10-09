// Resume Screener Test Interface JavaScript

class ResumeScreener {
    constructor() {
        this.jobDescriptions = [];
        this.uploadedResumes = [];
        this.rankingResults = null;
        this.selectedJobKey = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadJobDescriptions();
        this.updateUI();
    }
    
    setupEventListeners() {
        // File input change
        document.getElementById('fileInput').addEventListener('change', () => {
            this.updateUploadButton();
        });
        
        // Job selection change
        document.getElementById('jobSelect').addEventListener('change', (e) => {
            this.selectedJobKey = e.target.value;
            this.displayJobDescription();
            this.updateUI();
        });
        
        // Button clicks
        document.getElementById('uploadBtn').addEventListener('click', () => {
            this.uploadFiles();
        });
        
        document.getElementById('rankBtn').addEventListener('click', () => {
            this.rankResumes();
        });
        
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearAll();
        });
        
        document.getElementById('exportCsvBtn').addEventListener('click', () => {
            this.exportResults('csv');
        });
        
        document.getElementById('exportJsonBtn').addEventListener('click', () => {
            this.exportResults('json');
        });
        
        document.getElementById('showDetailsBtn').addEventListener('click', () => {
            this.toggleDetailedAnalysis();
        });
    }
    
    async loadJobDescriptions() {
        try {
            const response = await fetch('/api/job-descriptions');
            this.jobDescriptions = await response.json();
            
            const select = document.getElementById('jobSelect');
            select.innerHTML = '<option value="">Select a job...</option>';
            
            this.jobDescriptions.forEach(job => {
                const option = document.createElement('option');
                option.value = job.key;
                option.textContent = job.title;
                select.appendChild(option);
            });
            
            this.showToast('Job descriptions loaded', 'success');
        } catch (error) {
            this.showToast('Failed to load job descriptions', 'error');
            console.error('Error loading job descriptions:', error);
        }
    }
    
    updateUploadButton() {
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
        
        uploadBtn.disabled = !fileInput.files.length;
        
        if (fileInput.files.length > 0) {
            uploadBtn.innerHTML = `
                <i class="fas fa-cloud-upload-alt me-2"></i>
                Process ${fileInput.files.length} Resume${fileInput.files.length > 1 ? 's' : ''}
            `;
        } else {
            uploadBtn.innerHTML = `
                <i class="fas fa-cloud-upload-alt me-2"></i>
                Process Resumes
            `;
        }
    }
    
    displayJobDescription() {
        const jobDescSection = document.getElementById('jobDescriptionSection');
        
        if (!this.selectedJobKey) {
            jobDescSection.style.display = 'none';
            return;
        }
        
        const job = this.jobDescriptions.find(j => j.key === this.selectedJobKey);
        if (!job) return;
        
        document.getElementById('jobTitle').textContent = job.title;
        document.getElementById('jobDescription').textContent = job.description;
        
        // Required skills
        const requiredSkillsDiv = document.getElementById('requiredSkills');
        requiredSkillsDiv.innerHTML = '';
        job.required_skills.forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'skill-badge required';
            badge.textContent = skill;
            requiredSkillsDiv.appendChild(badge);
        });
        
        // Preferred skills
        const preferredSkillsDiv = document.getElementById('preferredSkills');
        preferredSkillsDiv.innerHTML = '';
        job.preferred_skills.forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'skill-badge preferred';
            badge.textContent = skill;
            preferredSkillsDiv.appendChild(badge);
        });
        
        jobDescSection.style.display = 'block';
    }
    
    async uploadFiles() {
        const fileInput = document.getElementById('fileInput');
        const files = fileInput.files;
        
        if (!files.length) {
            this.showToast('Please select files to upload', 'error');
            return;
        }
        
        this.showProgress('Uploading and processing files...', 0);
        
        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }
        
        try {
            // Simulate progress
            this.updateProgress('Uploading files...', 25);
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            this.updateProgress('Processing resumes...', 50);
            
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            
            const result = await response.json();
            this.uploadedResumes = result.results;
            
            this.updateProgress('Analysis complete!', 100);
            
            setTimeout(() => {
                this.hideProgress();
                this.displayUploadResults(result);
                this.updateUI();
                this.showToast(`Processed ${result.processed_count} resumes successfully`, 'success');
            }, 500);
            
        } catch (error) {
            this.hideProgress();
            this.showToast('Failed to upload files', 'error');
            console.error('Upload error:', error);
        }
    }
    
    displayUploadResults(result) {
        const uploadResults = document.getElementById('uploadResults');
        const uploadSummary = document.getElementById('uploadSummary');
        const uploadDetails = document.getElementById('uploadDetails');
        
        // Summary
        uploadSummary.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <div class="metric-card">
                        <div class="metric-value text-success">${result.processed_count}</div>
                        <div class="metric-label">Successfully Processed</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <div class="metric-value text-danger">${result.error_count}</div>
                        <div class="metric-label">Errors</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <div class="metric-value text-primary">${result.results.length}</div>
                        <div class="metric-label">Total Files</div>
                    </div>
                </div>
            </div>
        `;
        
        // Details
        let detailsHTML = '<div class="mt-3">';
        result.results.forEach((resume, index) => {
            const statusIcon = resume.error ? 
                '<i class="status-icon error fas fa-exclamation-circle"></i>' :
                '<i class="status-icon success fas fa-check-circle"></i>';
            
            detailsHTML += `
                <div class="resume-detail">
                    <h6>${statusIcon}${resume.original_filename || resume.file}</h6>
                    ${resume.error ? 
                        `<div class="text-danger"><small>${resume.error}</small></div>` :
                        `<div>
                            <small class="text-muted">
                                Skills detected: ${resume.preprocessed?.skills?.length || 0} |
                                Tokens: ${resume.preprocessed?.tokens?.length || 0}
                            </small>
                        </div>`
                    }
                </div>
            `;
        });
        detailsHTML += '</div>';
        
        uploadDetails.innerHTML = detailsHTML;
        uploadResults.style.display = 'block';
        
        // Hide welcome message
        document.getElementById('welcomeMessage').style.display = 'none';
    }
    
    async rankResumes() {
        if (!this.selectedJobKey) {
            this.showToast('Please select a job description first', 'error');
            return;
        }
        
        if (!this.uploadedResumes.length) {
            this.showToast('Please upload resumes first', 'error');
            return;
        }
        
        this.showProgress('Ranking candidates...', 0);
        
        try {
            this.updateProgress('Generating embeddings...', 25);
            
            const response = await fetch('/api/rank', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_key: this.selectedJobKey
                })
            });
            
            this.updateProgress('Computing similarity scores...', 50);
            
            if (!response.ok) {
                throw new Error('Ranking failed');
            }
            
            this.rankingResults = await response.json();
            
            this.updateProgress('Finalizing rankings...', 75);
            
            setTimeout(() => {
                this.updateProgress('Complete!', 100);
                setTimeout(() => {
                    this.hideProgress();
                    this.displayRankingResults();
                    this.updateUI();
                    this.showToast('Ranking completed successfully', 'success');
                }, 500);
            }, 500);
            
        } catch (error) {
            this.hideProgress();
            this.showToast('Failed to rank resumes', 'error');
            console.error('Ranking error:', error);
        }
    }
    
    displayRankingResults() {
        const rankingResults = document.getElementById('rankingResults');
        const rankingSummary = document.getElementById('rankingSummary');
        const rankingList = document.getElementById('rankingList');
        
        if (!this.rankingResults || this.rankingResults.error) {
            this.showToast('No ranking results to display', 'error');
            return;
        }
        
        const jobInfo = this.rankingResults.job_info;
        const results = this.rankingResults.ranked_results;
        
        // Summary
        rankingSummary.innerHTML = `
            <div class="alert alert-info">
                <h6><i class="fas fa-info-circle me-2"></i>Ranking for: ${jobInfo.title}</h6>
                <p class="mb-0">${this.rankingResults.total_resumes} candidates ranked using hybrid scoring (TF-IDF + Embeddings)</p>
            </div>
        `;
        
        // Ranking list
        let listHTML = '';
        results.forEach((result, index) => {
            if (result.error) {
                listHTML += `
                    <div class="card ranking-card mb-3">
                        <div class="card-body">
                            <div class="text-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                Error ranking ${result.file}: ${result.error}
                            </div>
                        </div>
                    </div>
                `;
                return;
            }
            
            const rankClass = index < 3 ? `rank-${index + 1}` : '';
            const scoreClass = result.hybrid_score >= 0.7 ? 'high' : 
                              result.hybrid_score >= 0.5 ? 'medium' : 'low';
            
            listHTML += `
                <div class="card ranking-card mb-3 ${rankClass}">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-1">
                                <div class="text-center">
                                    <div class="h4 mb-0 text-primary">${result.rank}</div>
                                    ${index === 0 ? '<i class="fas fa-trophy text-warning"></i>' :
                                      index === 1 ? '<i class="fas fa-medal text-secondary"></i>' :
                                      index === 2 ? '<i class="fas fa-award text-warning"></i>' : ''}
                                </div>
                            </div>
                            <div class="col-md-4">
                                <h6 class="mb-1">${result.file}</h6>
                                <small class="text-muted">
                                    Skills: ${result.skills?.length || 0} detected
                                </small>
                            </div>
                            <div class="col-md-3">
                                <div class="row text-center">
                                    <div class="col">
                                        <div class="score-indicator ${scoreClass}">
                                            ${result.hybrid_score?.toFixed(3) || 'N/A'}
                                        </div>
                                        <small class="text-muted">Hybrid</small>
                                    </div>
                                    <div class="col">
                                        <div class="small">
                                            TF-IDF: ${result.tfidf_score?.toFixed(3) || 'N/A'}<br>
                                            Embedding: ${result.embedding_score?.toFixed(3) || 'N/A'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="small">
                                    <div class="mb-1">
                                        <strong>Required Match:</strong> 
                                        ${result.required_skills_coverage || 0}% 
                                        (${result.required_skill_matches?.length || 0} skills)
                                    </div>
                                    <div class="coverage-bar">
                                        <div class="coverage-fill ${result.required_skills_coverage >= 70 ? '' : 
                                                                  result.required_skills_coverage >= 30 ? 'medium' : 'low'}" 
                                             style="width: ${result.required_skills_coverage || 0}%"></div>
                                    </div>
                                    <div>
                                        <strong>Preferred Match:</strong> 
                                        ${result.preferred_skills_coverage || 0}% 
                                        (${result.preferred_skill_matches?.length || 0} skills)
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-12">
                                <div class="small">
                                    <strong>Matched Skills:</strong>
                                    ${[...(result.required_skill_matches || []), ...(result.preferred_skill_matches || [])]
                                        .map(skill => `<span class="skill-badge matched">${skill}</span>`)
                                        .join('')
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        rankingList.innerHTML = listHTML;
        rankingResults.style.display = 'block';
    }
    
    toggleDetailedAnalysis() {
        const analysisDiv = document.getElementById('detailedAnalysis');
        const btn = document.getElementById('showDetailsBtn');
        
        if (analysisDiv.style.display === 'none' || !analysisDiv.style.display) {
            this.generateDetailedAnalysis();
            analysisDiv.style.display = 'block';
            btn.innerHTML = '<i class="fas fa-eye-slash me-1"></i>Hide Details';
        } else {
            analysisDiv.style.display = 'none';
            btn.innerHTML = '<i class="fas fa-eye me-1"></i>Show Details';
        }
    }
    
    generateDetailedAnalysis() {
        const analysisContent = document.getElementById('analysisContent');
        
        if (!this.rankingResults) return;
        
        const results = this.rankingResults.ranked_results.filter(r => !r.error);
        
        // Calculate statistics
        const hybridScores = results.map(r => r.hybrid_score);
        const tfidfScores = results.map(r => r.tfidf_score);
        const embeddingScores = results.map(r => r.embedding_score);
        
        const avgHybrid = (hybridScores.reduce((a, b) => a + b, 0) / hybridScores.length).toFixed(3);
        const avgTfidf = (tfidfScores.reduce((a, b) => a + b, 0) / tfidfScores.length).toFixed(3);
        const avgEmbedding = (embeddingScores.reduce((a, b) => a + b, 0) / embeddingScores.length).toFixed(3);
        
        let analysisHTML = `
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="analysis-chart">
                        <h6><i class="fas fa-chart-line me-2"></i>Score Statistics</h6>
                        <div class="row">
                            <div class="col">
                                <div class="metric-value">${avgHybrid}</div>
                                <div class="metric-label">Avg Hybrid</div>
                            </div>
                            <div class="col">
                                <div class="metric-value">${avgTfidf}</div>
                                <div class="metric-label">Avg TF-IDF</div>
                            </div>
                            <div class="col">
                                <div class="metric-value">${avgEmbedding}</div>
                                <div class="metric-label">Avg Embedding</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="analysis-chart">
                        <h6><i class="fas fa-skills me-2"></i>Skill Analysis</h6>
                        <div class="row">
        `;
        
        // Skill frequency analysis
        const allSkills = {};
        results.forEach(result => {
            (result.skills || []).forEach(skill => {
                allSkills[skill] = (allSkills[skill] || 0) + 1;
            });
        });
        
        const topSkills = Object.entries(allSkills)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 6);
        
        topSkills.forEach(([skill, count]) => {
            const percentage = (count / results.length * 100).toFixed(1);
            analysisHTML += `
                <div class="col-md-4 mb-2">
                    <div class="small">
                        <strong>${skill}</strong><br>
                        <div class="coverage-bar">
                            <div class="coverage-fill" style="width: ${percentage}%"></div>
                        </div>
                        ${count}/${results.length} resumes (${percentage}%)
                    </div>
                </div>
            `;
        });
        
        analysisHTML += `
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Detailed resume breakdown
        analysisHTML += `
            <div class="analysis-chart">
                <h6><i class="fas fa-list me-2"></i>Detailed Resume Breakdown</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Resume</th>
                                <th>Hybrid Score</th>
                                <th>TF-IDF</th>
                                <th>Embedding</th>
                                <th>Skills Match</th>
                                <th>Total Skills</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        results.forEach(result => {
            analysisHTML += `
                <tr>
                    <td><strong>${result.rank}</strong></td>
                    <td>${result.file}</td>
                    <td><span class="badge bg-primary">${result.hybrid_score?.toFixed(3) || 'N/A'}</span></td>
                    <td>${result.tfidf_score?.toFixed(3) || 'N/A'}</td>
                    <td>${result.embedding_score?.toFixed(3) || 'N/A'}</td>
                    <td>${result.total_skill_matches || 0}</td>
                    <td>${result.skills?.length || 0}</td>
                </tr>
            `;
        });
        
        analysisHTML += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        analysisContent.innerHTML = analysisHTML;
    }
    
    async exportResults(format) {
        if (!this.uploadedResumes.length) {
            this.showToast('No data to export', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/export/${format}`);
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `resume_analysis_${new Date().getTime()}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showToast(`Results exported as ${format.toUpperCase()}`, 'success');
        } catch (error) {
            this.showToast('Export failed', 'error');
            console.error('Export error:', error);
        }
    }
    
    async clearAll() {
        if (confirm('Are you sure you want to clear all data? This will reset the interface.')) {
            try {
                await fetch('/api/clear-session', { method: 'POST' });
                
                // Reset UI
                this.uploadedResumes = [];
                this.rankingResults = null;
                this.selectedJobKey = null;
                
                // Reset form
                document.getElementById('fileInput').value = '';
                document.getElementById('jobSelect').value = '';
                
                // Hide sections
                document.getElementById('jobDescriptionSection').style.display = 'none';
                document.getElementById('uploadResults').style.display = 'none';
                document.getElementById('rankingResults').style.display = 'none';
                document.getElementById('detailedAnalysis').style.display = 'none';
                
                // Show welcome message
                document.getElementById('welcomeMessage').style.display = 'block';
                
                this.updateUI();
                this.updateStatus('Ready to process resumes');
                this.showToast('Interface cleared', 'success');
            } catch (error) {
                this.showToast('Failed to clear session', 'error');
                console.error('Clear error:', error);
            }
        }
    }
    
    updateUI() {
        const hasFiles = document.getElementById('fileInput').files.length > 0;
        const hasJob = this.selectedJobKey !== null;
        const hasUploads = this.uploadedResumes.length > 0;
        const hasRankings = this.rankingResults !== null;
        
        document.getElementById('uploadBtn').disabled = !hasFiles;
        document.getElementById('rankBtn').disabled = !hasJob || !hasUploads;
        document.getElementById('exportCsvBtn').disabled = !hasUploads;
        document.getElementById('exportJsonBtn').disabled = !hasUploads;
        
        this.updateUploadButton();
        
        // Update status
        if (hasRankings) {
            this.updateStatus(`Ranked ${this.rankingResults.total_resumes} resumes for ${this.rankingResults.job_info.title}`);
        } else if (hasUploads) {
            this.updateStatus(`${this.uploadedResumes.filter(r => !r.error).length} resumes processed and ready for ranking`);
        } else if (hasFiles) {
            this.updateStatus(`${document.getElementById('fileInput').files.length} files selected for upload`);
        } else if (hasJob) {
            this.updateStatus(`Job "${this.jobDescriptions.find(j => j.key === this.selectedJobKey)?.title}" selected`);
        } else {
            this.updateStatus('Ready to process resumes');
        }
    }
    
    updateStatus(message) {
        document.getElementById('statusContent').innerHTML = `
            <div class="text-muted">
                <i class="fas fa-circle-info me-1"></i>
                ${message}
            </div>
        `;
    }
    
    showProgress(message, percent) {
        const progressSection = document.getElementById('progressSection');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        progressText.textContent = message;
        progressBar.style.width = percent + '%';
        progressSection.style.display = 'block';
    }
    
    updateProgress(message, percent) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        progressText.textContent = message;
        progressBar.style.width = percent + '%';
    }
    
    hideProgress() {
        document.getElementById('progressSection').style.display = 'none';
    }
    
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-body">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 
                                  type === 'error' ? 'exclamation-circle' : 
                                  'info-circle'} me-2"></i>
                ${message}
            </div>
        `;
        
        container.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.style.opacity = '1';
        }, 100);
        
        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.resumeScreener = new ResumeScreener();
});

// Add some helpful CSS for toasts
const toastStyles = document.createElement('style');
toastStyles.textContent = `
    .toast {
        opacity: 0;
        transition: opacity 0.3s ease;
        margin-bottom: 0.5rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
        color: white;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    }
    
    .toast.info {
        background: linear-gradient(135deg, #0dcaf0, #0d6efd);
    }
`;
document.head.appendChild(toastStyles);