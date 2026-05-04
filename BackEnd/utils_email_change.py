from flask_mail import Message
from flask import current_app
from datetime import datetime

def send_email_change_code_email(mail, new_email, code, user_name=''):
    """Send email change verification code to the NEW email address"""
    try:
        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .code-box {{
                    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                    border: 2px solid #3b82f6;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #1e3a8a;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .footer {{
                    background: #f9fafb;
                    padding: 20px 30px;
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 Sougui</h1>
                    <p>Code de vérification - Changement d'email</p>
                </div>
                <div class="content">
                    <p>Bonjour {user_name},</p>
                    <p>Vous avez demandé à changer votre adresse email. Pour confirmer cette nouvelle adresse, veuillez utiliser le code ci-dessous.</p>
                    
                    <div class="code-box">
                        <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">Votre code de vérification</p>
                        <div class="code">{code}</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⏰ Important:</strong> Ce code expire dans <strong>15 minutes</strong>.
                    </div>
                    
                    <p>Entrez ce code dans l'application pour confirmer votre nouvelle adresse email.</p>
                    
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        Si vous n'avez pas demandé ce changement, veuillez ignorer cet email.
                    </p>
                </div>
                <div class="footer">
                    <p><strong>Sougui - Produits Artisanaux Tunisiens</strong></p>
                    <p>© 2024 Sougui. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        text_body = f'''Bonjour {user_name},

Vous avez demandé à changer votre adresse email.

Votre code de vérification est: {code}

Ce code expire dans 15 minutes.

Si vous n'avez pas demandé ce changement, veuillez ignorer cet email.

Cordialement,
L'équipe Sougui'''
        
        msg = Message(
            subject='📧 Code de vérification - Changement d\'email',
            sender=('Sougui Platform', current_app.config['MAIL_USERNAME']),
            recipients=[new_email],
            body=text_body,
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_email_changed_confirmation_email(mail, old_email, new_email, user_name=''):
    """Send confirmation to OLD email that the email was changed"""
    try:
        now = datetime.utcnow()
        date_str = now.strftime('%d/%m/%Y')
        time_str = now.strftime('%H:%M:%S')
        
        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .success-box {{
                    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                    border: 2px solid #10b981;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .success-icon {{
                    font-size: 48px;
                    margin-bottom: 10px;
                }}
                .info-box {{
                    background: #f9fafb;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                    border-bottom: 1px solid #e5e7eb;
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .warning {{
                    background: #fee2e2;
                    border-left: 4px solid #ef4444;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .footer {{
                    background: #f9fafb;
                    padding: 20px 30px;
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Sougui</h1>
                    <p>Email changé avec succès</p>
                </div>
                <div class="content">
                    <p>Bonjour {user_name},</p>
                    
                    <div class="success-box">
                        <div class="success-icon">✅</div>
                        <h2 style="margin: 0; color: #065f46;">Email modifié</h2>
                        <p style="margin: 10px 0 0 0; color: #047857;">Votre adresse email a été changée avec succès.</p>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-row">
                            <strong>Ancienne adresse:</strong>
                            <span>{old_email}</span>
                        </div>
                        <div class="info-row">
                            <strong>Nouvelle adresse:</strong>
                            <span>{new_email}</span>
                        </div>
                        <div class="info-row">
                            <strong>Date:</strong>
                            <span>{date_str}</span>
                        </div>
                        <div class="info-row">
                            <strong>Heure:</strong>
                            <span>{time_str} UTC</span>
                        </div>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Attention:</strong> Si ce n'était pas vous qui avez effectué ce changement, veuillez contacter immédiatement notre équipe de support.
                    </div>
                    
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        Ceci est un email de notification envoyé à votre ancienne adresse. Toutes les futures communications seront envoyées à votre nouvelle adresse.
                    </p>
                </div>
                <div class="footer">
                    <p><strong>Sougui - Produits Artisanaux Tunisiens</strong></p>
                    <p>© 2024 Sougui. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        text_body = f'''Bonjour {user_name},

Votre adresse email a été changée avec succès.

Ancienne adresse: {old_email}
Nouvelle adresse: {new_email}
Date: {date_str}
Heure: {time_str} UTC

Si ce n'était pas vous, contactez-nous immédiatement.

Cordialement,
L'équipe Sougui'''
        
        msg = Message(
            subject='✅ Email changé avec succès - Sougui',
            sender=('Sougui Platform', current_app.config['MAIL_USERNAME']),
            recipients=[old_email],
            body=text_body,
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
