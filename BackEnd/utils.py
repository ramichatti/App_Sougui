import random
import string
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app

def generate_reset_code():
    """Generate a 6-digit reset code"""
    return ''.join(random.choices(string.digits, k=6))

def send_reset_code_email(mail, user_email, reset_code, user_name=''):
    """Send reset code via email"""
    try:
        # Create HTML email
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
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Sougui</h1>
                    <p>Réinitialisation de mot de passe</p>
                </div>
                <div class="content">
                    <p>Bonjour {user_name},</p>
                    <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte Sougui.</p>
                    
                    <div class="code-box">
                        <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">Votre code de vérification</p>
                        <div class="code">{reset_code}</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⏰ Important:</strong> Ce code expire dans <strong>15 minutes</strong>.
                    </div>
                    
                    <p>Entrez ce code dans l'application pour continuer la réinitialisation de votre mot de passe.</p>
                    
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email. 
                        Votre mot de passe restera inchangé.
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
        
        # Plain text version
        text_body = f'''Bonjour {user_name},

Vous avez demandé la réinitialisation de votre mot de passe.

Votre code de vérification est: {reset_code}

Ce code expire dans 15 minutes.

Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email.

Cordialement,
L'équipe Sougui'''
        
        msg = Message(
            subject='🔐 Code de réinitialisation - Sougui',
            sender=('Sougui Platform', current_app.config['MAIL_USERNAME']),
            recipients=[user_email],
            body=text_body,
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_privilege_notification_email(mail, user_email, user_name, privilege_name, dashboard_name, role_name):
    """Notify a user that a new privilege (dashboard access) was granted to their role."""
    try:
        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 30px; }}
                .info-box {{ background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 2px solid #3b82f6; border-radius: 10px; padding: 20px; margin: 24px 0; }}
                .info-box h2 {{ color: #1e3a8a; margin: 0 0 12px 0; font-size: 18px; }}
                .info-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #bfdbfe; font-size: 14px; }}
                .info-row:last-child {{ border-bottom: none; }}
                .info-label {{ color: #64748b; font-weight: 600; }}
                .info-value {{ color: #1e3a8a; font-weight: 700; }}
                .footer {{ background: #f9fafb; padding: 20px 30px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Sougui</h1>
                    <p>Nouveau privilège accordé</p>
                </div>
                <div class="content">
                    <p>Bonjour {user_name},</p>
                    <p>Un nouveau privilège d'accès a été accordé à votre rôle sur la plateforme Sougui.</p>
                    <div class="info-box">
                        <h2>Détails du privilège</h2>
                        <div class="info-row">
                            <span class="info-label">Privilège :</span>
                            <span class="info-value">{privilege_name}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Dashboard :</span>
                            <span class="info-value">{dashboard_name}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Rôle :</span>
                            <span class="info-value">{role_name}</span>
                        </div>
                    </div>
                    <p>Vous pouvez désormais accéder à ce dashboard depuis votre espace Sougui.</p>
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        Si vous pensez avoir reçu cet email par erreur, contactez votre administrateur.
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

Un nouveau privilège a été accordé à votre rôle.

Privilège : {privilege_name}
Dashboard : {dashboard_name}
Rôle : {role_name}

Connectez-vous à Sougui pour y accéder.

Cordialement,
L\'équipe Sougui'''

        msg = Message(
            subject='Nouveau privilège accordé - Sougui',
            sender=('Sougui Platform', current_app.config['MAIL_USERNAME']),
            recipients=[user_email],
            body=text_body,
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending privilege notification email: {str(e)}")
        return False


def is_code_expired(expiration_time):
    """Check if reset code is expired"""
    if not expiration_time:
        return True
    return datetime.utcnow() > expiration_time

def send_password_change_code_email(mail, user_email, code, user_name=''):
    """Send password change verification code via email"""
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
                    <h1>🔐 Sougui</h1>
                    <p>Code de vérification - Changement de mot de passe</p>
                </div>
                <div class="content">
                    <p>Bonjour {user_name},</p>
                    <p>Vous avez demandé à changer votre mot de passe. Pour des raisons de sécurité, veuillez confirmer cette action avec le code ci-dessous.</p>
                    
                    <div class="code-box">
                        <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">Votre code de vérification</p>
                        <div class="code">{code}</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⏰ Important:</strong> Ce code expire dans <strong>15 minutes</strong>.
                    </div>
                    
                    <p>Entrez ce code dans l'application pour continuer le changement de votre mot de passe.</p>
                    
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        Si vous n'avez pas demandé ce changement, veuillez ignorer cet email et votre mot de passe restera inchangé.
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

Vous avez demandé à changer votre mot de passe.

Votre code de vérification est: {code}

Ce code expire dans 15 minutes.

Si vous n'avez pas demandé ce changement, veuillez ignorer cet email.

Cordialement,
L'équipe Sougui'''
        
        msg = Message(
            subject='🔐 Code de vérification - Changement de mot de passe',
            sender=('Sougui Platform', current_app.config['MAIL_USERNAME']),
            recipients=[user_email],
            body=text_body,
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_password_changed_confirmation_email(mail, user_email, user_name=''):
    """Send password changed confirmation email"""
    try:
        from datetime import datetime
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
                    <p>Mot de passe changé avec succès</p>
                </div>
                <div class="content">
                    <p>Bonjour {user_name},</p>
                    
                    <div class="success-box">
                        <div class="success-icon">✅</div>
                        <h2 style="margin: 0; color: #065f46;">Mot de passe modifié</h2>
                        <p style="margin: 10px 0 0 0; color: #047857;">Votre mot de passe a été changé avec succès.</p>
                    </div>
                    
                    <div class="info-box">
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
                        Pour votre sécurité, nous vous recommandons d'utiliser un mot de passe fort et unique.
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

Votre mot de passe a été changé avec succès.

Date: {date_str}
Heure: {time_str} UTC

Si ce n'était pas vous, contactez-nous immédiatement.

Cordialement,
L'équipe Sougui'''
        
        msg = Message(
            subject='✅ Mot de passe changé avec succès - Sougui',
            sender=('Sougui Platform', current_app.config['MAIL_USERNAME']),
            recipients=[user_email],
            body=text_body,
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
