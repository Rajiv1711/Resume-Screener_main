import React from "react";
import { Link, useNavigate } from "react-router-dom";
import ParallaxHero from "../components/ParallaxHero";
import GlassCard from "../components/GlassCard";

const Home = () => {
  const navigate = useNavigate();

  const Feature = ({ icon, title, desc }) => (
    <div className="col-md-4 mb-4">
      <div className="p-4 h-100 rounded" style={{
        backgroundColor: 'var(--bg-tertiary)',
        border: '1px solid var(--border-primary)'
      }}>
        <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor" className="mb-3" style={{color: 'var(--accent-primary)'}}>
          <path d={icon} />
        </svg>
        <h6 className="mb-1" style={{color: 'var(--text-primary)'}}>{title}</h6>
        <p className="small mb-0" style={{color: 'var(--text-secondary)'}}>{desc}</p>
      </div>
    </div>
  );

  return (
    <div className="page-container">
      <ParallaxHero
        title="Resume Screener"
        subtitle="Upload, rank, and analyze resumes with an elegant AI-powered workflow"
      />

      {/* Quick actions */}
      <div className="row g-4 mb-4">
        <div className="col-lg-7">
          <GlassCard>
            <div className="d-flex flex-column flex-md-row align-items-start align-items-md-center justify-content-between gap-3">
              <div>
                <h4 className="mb-2" style={{color: 'var(--text-primary)'}}>Get Started</h4>
                <p className="mb-0" style={{color: 'var(--text-secondary)'}}>Begin by uploading resumes or jump to your dashboard to rank and explore insights.</p>
              </div>
              <div className="d-flex gap-3 flex-wrap">
                <Link to="/upload" className="btn btn-custom-primary d-flex align-items-center">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                    <path d="M9,16V10H5L12,3L19,10H15V16H9M5,20V18H19V20H5Z" />
                  </svg>
                  Upload Resumes
                </Link>
                <button className="btn btn-custom-secondary d-flex align-items-center" onClick={() => navigate('/dashboard')}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                    <path d="M13,3V9H21V3M13,21H21V11H13M3,21H11V15H3M3,13H11V3H3V13Z" />
                  </svg>
                  Go to Dashboard
                </button>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="mt-4">
            <h5 className="mb-3" style={{color: 'var(--text-primary)'}}>How it works</h5>
            <div className="row g-3">
              {[{
                step: '1',
                title: 'Upload resumes',
                desc: 'Add individual files or a ZIP archive. Supported: PDF, DOC/DOCX, TXT, ZIP.'
              },{
                step: '2',
                title: 'Provide a job description',
                desc: 'Paste the JD on the dashboard for tailored ranking.'
              },{
                step: '3',
                title: 'Review results and export',
                desc: 'Analyze ranked candidates, insights, and export CSV/XLSX/PDF.'
              }].map((s, i) => (
                <div className="col-md-4" key={i}>
                  <div className="p-3 rounded h-100" style={{backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-primary)'}}>
                    <div className="d-flex align-items-center mb-2">
                      <span className="me-2 d-inline-flex align-items-center justify-content-center" style={{
                        width: 28, height: 28, borderRadius: 999,
                        background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))', color: '#0b1220', fontWeight: 700
                      }}>{s.step}</span>
                      <strong style={{color: 'var(--text-primary)'}}>{s.title}</strong>
                    </div>
                    <div className="small" style={{color: 'var(--text-secondary)'}}>{s.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>

        <div className="col-lg-5">
          <GlassCard>
            <h5 className="mb-3" style={{color: 'var(--text-primary)'}}>Why choose this platform?</h5>
            <div className="row">
              <Feature icon="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" title="Flexible uploads" desc="Upload PDFs, Word docs, plain text, or entire ZIP archives." />
              <Feature icon="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" title="AI ranking" desc="Hybrid ranking with insights for faster shortlisting." />
              <Feature icon="M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21Z" title="Actionable analytics" desc="Visualize scores and export reports in multiple formats." />
            </div>

            <div className="mt-3 p-3 rounded" style={{
              backgroundColor: 'rgba(79, 209, 197, 0.08)',
              border: '1px dashed var(--accent-primary)'
            }}>
              <div className="d-flex align-items-center">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" className="me-2" style={{color: 'var(--accent-primary)'}}>
                  <path d="M12,2A10,10 0 0,1 22,12C22,17.5 17.5,22 12,22C6.5,22 2,17.5 2,12C2,6.5 6.5,2 12,2M11,17H13V11H11V17M11,9H13V7H11V9Z" />
                </svg>
                <small style={{color: 'var(--text-secondary)'}}>Tip: Use Sessions (top nav) to organize uploads by job role or hiring round.</small>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Supported formats */}
      <div className="row mt-4">
        <div className="col-12 text-center">
          <h6 className="mb-3" style={{color: 'var(--text-secondary)'}}>Supported formats</h6>
          <div className="d-flex flex-wrap justify-content-center gap-3">
            {[
              { name: 'PDF', icon: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z' },
              { name: 'DOC/DOCX', icon: 'M6,2A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2H6Z' },
              { name: 'TXT', icon: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z' },
              { name: 'ZIP', icon: 'M14,12V19.88C14.04,20.18 13.94,20.5 13.71,20.71C13.32,21.1 12.69,21.1 12.3,20.71L10.59,19H10V12H14M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4A2,2 0 0,1 6,2Z' }
            ].map((f, i) => (
              <span key={i} className="px-3 py-2 rounded" style={{
                backgroundColor: 'var(--bg-tertiary)',
                border: '1px solid var(--border-primary)',
                color: 'var(--text-secondary)'
              }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" className="me-2">
                  <path d={f.icon} />
                </svg>
                {f.name}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
