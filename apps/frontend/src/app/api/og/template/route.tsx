import { ImageResponse } from 'next/og';
import { NextRequest } from 'next/server';
import { carbonScope } from '@/lib/design-tokens';

// Node runtime: Edge + @vercel/og ImageResponse can hit incorrect `react` resolution
// ("react-server" condition) during `next build` static analysis.
export const runtime = 'nodejs';

const ogTheme = {
  bgBase: carbonScope.colors.background,
  bgAlt: carbonScope.colors.backgroundAlt,
  bgSubtle: carbonScope.colors.backgroundSubtle,
  textPrimary: carbonScope.colors.textPrimary,
  textSecondary: carbonScope.colors.textSecondary,
  textMuted: carbonScope.colors.textMuted,
  border: carbonScope.colors.border,
  info: carbonScope.colors.info,
  infoLight: carbonScope.colors.infoLight,
  fontBody: carbonScope.typography.fontBody,
} as const;

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const shareId = searchParams.get('shareId');

    if (!shareId) {
      return new Response('Missing shareId parameter', { status: 400 });
    }

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, '') || 'http://localhost:8000/v1';

    const templateResponse = await fetch(
      `${backendUrl}/templates/public/${shareId}`
    );

    if (!templateResponse.ok) {
      throw new Error('Template not found');
    }

    const template = await templateResponse.json();
    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: ogTheme.bgBase,
            backgroundImage: `linear-gradient(to bottom right, ${ogTheme.bgAlt}, ${ogTheme.bgBase})`,
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.08) 1px, transparent 1px)`,
              backgroundSize: '40px 40px',
            }}
          />
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '64px',
              textAlign: 'center',
              fontFamily: ogTheme.fontBody,
            }}
          >
            {template.is_CarbonScope_team && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  backgroundColor: `${ogTheme.info}20`,
                  borderRadius: '9999px',
                  padding: '8px 16px',
                  marginBottom: '24px',
                  border: `1px solid ${ogTheme.info}40`,
                }}
              >
                <span style={{ color: ogTheme.infoLight, fontSize: '14px', fontWeight: 600 }}>
                  ✨ Official Template
                </span>
              </div>
            )}
            <div
              style={{
                width: '120px',
                height: '120px',
                borderRadius: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '64px',
                marginBottom: '32px',
              }}
            >
              🤖
            </div>
            <h1
              style={{
                fontSize: '56px',
                fontWeight: 700,
                color: ogTheme.textPrimary,
                marginBottom: '16px',
                lineHeight: 1.1,
                maxWidth: '900px',
              }}
            >
              {template.name}
            </h1>
            <p
              style={{
                fontSize: '24px',
                color: ogTheme.textSecondary,
                marginBottom: '40px',
                maxWidth: '800px',
                lineHeight: 1.4,
              }}
            >
              {template.description || 'An AI agent template ready to be customized for your needs.'}
            </p>
            <div
              style={{
                display: 'flex',
                gap: '40px',
                alignItems: 'center',
                marginBottom: '40px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: ogTheme.textMuted, fontSize: '18px' }}>by</span>
                <span style={{ color: ogTheme.textPrimary, fontSize: '18px', fontWeight: 600 }}>
                  {template.creator_name || 'Anonymous'}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: ogTheme.textPrimary, fontSize: '18px', fontWeight: 600 }}>
                  {template.download_count}
                </span>
                <span style={{ color: ogTheme.textMuted, fontSize: '18px' }}>installs</span>
              </div>
              {template.mcp_requirements && template.mcp_requirements.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ color: ogTheme.textPrimary, fontSize: '18px', fontWeight: 600 }}>
                    {template.mcp_requirements.length}
                  </span>
                  <span style={{ color: ogTheme.textMuted, fontSize: '18px' }}>integrations</span>
                </div>
              )}
            </div>
            {template.tags && template.tags.length > 0 && (
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '40px' }}>
                {template.tags.slice(0, 5).map((tag: string, index: number) => (
                  <div
                    key={index}
                    style={{
                      backgroundColor: ogTheme.bgSubtle,
                      borderRadius: '8px',
                      padding: '6px 12px',
                      fontSize: '16px',
                      color: ogTheme.textSecondary,
                      border: `1px solid ${ogTheme.border}`,
                    }}
                  >
                    {tag}
                  </div>
                ))}
              </div>
            )}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                position: 'absolute',
                bottom: '40px',
              }}
            >
              <span style={{ color: ogTheme.textMuted, fontSize: '20px' }}>CarbonScope</span>
              <span style={{ color: ogTheme.border, fontSize: '20px' }}>•</span>
              <span style={{ color: ogTheme.textMuted, fontSize: '20px' }}>AI Agent Marketplace</span>
            </div>
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  } catch (error) {
    console.error('OG Image generation error:', error);
    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: ogTheme.bgBase,
            backgroundImage: `linear-gradient(to bottom right, ${ogTheme.bgAlt}, ${ogTheme.bgBase})`,
          }}
        >
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              fontFamily: ogTheme.fontBody,
            }}
          >
            <div
              style={{
                fontSize: '80px',
                marginBottom: '24px',
              }}
            >
              🤖
            </div>
            <h1
              style={{
                fontSize: '48px',
                fontWeight: 700,
                color: ogTheme.textPrimary,
                marginBottom: '16px',
              }}
            >
              AI Agent Template
            </h1>
            <p
              style={{
                fontSize: '20px',
                color: ogTheme.textSecondary,
              }}
            >
              Discover powerful AI agents on CarbonScope
            </p>
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  }
} 