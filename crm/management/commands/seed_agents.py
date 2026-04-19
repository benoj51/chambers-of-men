"""
Management command to seed default AgentConfig and EmailTemplate records.

Usage:
    python manage.py seed_agents
"""

from django.core.management.base import BaseCommand
from crm.models import AgentConfig, EmailTemplate


class Command(BaseCommand):
    help = 'Seed default agent configurations and email templates'

    def handle(self, *args, **options):
        self._seed_agent_configs()
        self._seed_email_templates()
        self.stdout.write(self.style.SUCCESS('Agent framework seeded successfully.'))

    def _seed_agent_configs(self):
        agents = [
            {
                'agent_name': 'onboarding',
                'is_active': True,
                'config': {
                    'welcome_delay_minutes': 0,
                    'follow_up_days': [2, 5, 10],
                    'stalled_grace_days': 7,
                },
            },
            {
                'agent_name': 'crm_pipeline',
                'is_active': True,
                'config': {
                    'inactive_threshold_days': 90,
                },
            },
            {
                'agent_name': 'event_manager',
                'is_active': True,
                'config': {
                    'reminder_days': [7, 1],
                },
            },
            {
                'agent_name': 'iron_circle',
                'is_active': True,
                'config': {
                    'max_circle_size': 5,
                    'match_by_city': True,
                },
            },
            {
                'agent_name': 'social_media',
                'is_active': False,  # Off by default until Buffer API is configured
                'config': {
                    'platforms': ['instagram', 'tiktok', 'youtube'],
                },
            },
            {
                'agent_name': 'leadership',
                'is_active': True,
                'config': {
                    'min_activities_for_promotion': 5,
                    'min_events_for_promotion': 2,
                },
            },
        ]

        for agent_data in agents:
            obj, created = AgentConfig.objects.get_or_create(
                agent_name=agent_data['agent_name'],
                defaults={
                    'is_active': agent_data['is_active'],
                    'config': agent_data['config'],
                }
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"  {status}: {obj}")

    def _seed_email_templates(self):
        templates = [
            {
                'template_key': 'welcome',
                'subject': 'Welcome to Chambers of Men, {{ first_name }}',
                'body_html': '''<div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #0D2137; padding: 30px; text-align: center;">
        <h1 style="color: #1A6B5A; margin: 0; font-size: 28px;">Chambers of Men</h1>
        <p style="color: #E8F5F0; margin: 10px 0 0; font-style: italic;">Awaken. Equip. Deploy.</p>
    </div>

    <div style="padding: 30px; background: #ffffff;">
        <p>Dear {{ first_name }},</p>

        <p>Thank you for your interest in joining Chambers of Men. We are honoured that you have taken this step.</p>

        <p>Chambers of Men is a movement dedicated to restoring men to the image of God through structured leadership, doctrinal purity, and strategic deployment. Here in the Hackney Iron Circle, we are building something real - a brotherhood that sharpens, supports, and sends.</p>

        <p>Here is what happens next:</p>

        <ol>
            <li>A member of our team will review your details</li>
            <li>We will reach out to schedule a brief introductory conversation</li>
            <li>You will be matched with an Iron Circle - a small group of 3 to 5 men who meet weekly</li>
        </ol>

        <p>In the meantime, feel free to reply to this email with any questions.</p>

        <p style="margin-top: 30px;"><strong>Keep climbing, brother.</strong></p>

        <p>Chambers of Men Team</p>
    </div>

    <div style="background: #0D2137; padding: 15px; text-align: center;">
        <p style="color: #E8F5F0; margin: 0; font-size: 12px;">You are not alone, brother.</p>
    </div>
</div>''',
            },
            {
                'template_key': 'follow_up_day_2',
                'subject': '{{ first_name }}, a quick question from Chambers of Men',
                'body_html': '''<div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #0D2137; padding: 30px; text-align: center;">
        <h1 style="color: #1A6B5A; margin: 0; font-size: 28px;">Chambers of Men</h1>
    </div>

    <div style="padding: 30px; background: #ffffff;">
        <p>Dear {{ first_name }},</p>

        <p>Thank you again for expressing interest in Chambers of Men. We wanted to follow up with a quick question to help us serve you better.</p>

        <p>Could you tell us a little about your faith journey? Specifically:</p>

        <ul>
            <li>Are you currently attending a local church?</li>
            <li>How long have you been walking with Christ?</li>
            <li>What drew you to Chambers of Men?</li>
        </ul>

        <p>There are no wrong answers - we simply want to understand where you are so we can support you well. Just reply to this email with your thoughts.</p>

        <p style="margin-top: 30px;"><strong>Keep climbing, brother.</strong></p>

        <p>Chambers of Men Team</p>
    </div>

    <div style="background: #0D2137; padding: 15px; text-align: center;">
        <p style="color: #E8F5F0; margin: 0; font-size: 12px;">You are not alone, brother.</p>
    </div>
</div>''',
            },
            {
                'template_key': 'follow_up_day_5',
                'subject': '{{ first_name }}, your Iron Circle awaits',
                'body_html': '''<div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #0D2137; padding: 30px; text-align: center;">
        <h1 style="color: #1A6B5A; margin: 0; font-size: 28px;">Chambers of Men</h1>
    </div>

    <div style="padding: 30px; background: #ffffff;">
        <p>Dear {{ first_name }},</p>

        <p>We hope this message finds you well. We wanted to share more about what joining Chambers of Men looks like in practice.</p>

        <p><strong>The Iron Circle</strong> is the heartbeat of the movement. It is a small group of 3 to 5 men who meet weekly to:</p>

        <ul>
            <li>Study Scripture and grow in doctrine</li>
            <li>Hold each other accountable</li>
            <li>Support one another through life's challenges</li>
            <li>Prepare for leadership and service</li>
        </ul>

        <p>We would love to invite you for a brief introductory conversation - just 15 to 20 minutes - so we can learn more about you and answer any questions. This is not an interview; it is a conversation between brothers.</p>

        <p>If you are interested, simply reply to this email with a few times that work for you, and we will arrange a call.</p>

        <p style="margin-top: 30px;"><strong>Keep climbing, brother.</strong></p>

        <p>Chambers of Men Team</p>
    </div>

    <div style="background: #0D2137; padding: 15px; text-align: center;">
        <p style="color: #E8F5F0; margin: 0; font-size: 12px;">You are not alone, brother.</p>
    </div>
</div>''',
            },
            {
                'template_key': 'follow_up_day_10',
                'subject': '{{ first_name }}, we have not forgotten about you',
                'body_html': '''<div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #0D2137; padding: 30px; text-align: center;">
        <h1 style="color: #1A6B5A; margin: 0; font-size: 28px;">Chambers of Men</h1>
    </div>

    <div style="padding: 30px; background: #ffffff;">
        <p>Dear {{ first_name }},</p>

        <p>We reached out a few times over the past week and wanted to check in one more time.</p>

        <p>We understand life gets busy. If now is not the right time, that is completely fine - the door remains open whenever you are ready.</p>

        <p>If you are still interested in joining Chambers of Men, simply reply to this email or reach out at any time. We would be glad to hear from you.</p>

        <p>Until then, we will keep you in our prayers.</p>

        <p style="margin-top: 30px;"><strong>You are not alone, brother.</strong></p>

        <p>Chambers of Men Team</p>
    </div>

    <div style="background: #0D2137; padding: 15px; text-align: center;">
        <p style="color: #E8F5F0; margin: 0; font-size: 12px;">Keep climbing, brother.</p>
    </div>
</div>''',
            },
            {
	�[\]W��^IΈ	�[�\��Y]�ܙ[Z[�\���	��X��X�	Έ	ԙ[Z[�\��[�\��۝�\��][ۈ�]H�[X�\��وY[��[ܜ�����	؛�W�[	Έ	���]��[OH��۝Y�[Z[N��[ܙ�XK�\�Y��X^]�Y���X\��[��]]��Y[�Έ�ȏ��]��[OH��X��ܛ�[����L���Y[�Έ��^X[Yێ��[�\�ȏ��H�[OH���܎��PM��PN�X\��[����۝\�^�N��ȏ�H�[X�\��وY[��O���]����]��[OH�Y[�Έ���X��ܛ�[��ٙ�����ȏ���X\����\��ۘ[YH_K�����\�\�H��Y[�H�[Z[�\�][�\�[���X�ܞH�۝�\��][ۈ�]H�[X�\��وY[�\���Y[Y�܈��ۙϞ��[�\��Y]��]H_O���ۙϋ������\��[�HH�[^YMH��Z[�]H�]�\�H�H�]�ۛ��[�H[�[���\�[�H]Y\�[ۜ�[�HX^H]�HX��]H[ݙ[Y[�[�H\�ۈ�\��K������Y�[�H�YY��\��Y[K�[\H�\H�\�[XZ[[��H�[�ܝ]�]���������[���ܝ�\���XZ�[���][�K���\�������[OH�X\��[�]���ȏ���ۙϒ�Y\�[X�[�����\�����ۙϏ�����H�[X�\��وY[�X[O����]����]��[OH��X��ܛ�[����L���Y[�ΈM\�^X[Yێ��[�\�ȏ���[OH���܎��N�Q��X\��[����۝\�^�N�L�ȏ�[�H\�H��[ۙK���\������]����]������K�	�[\]W��^IΈ	�]�[�ܙ[Z[�\���	��	��X��X�	Έ	���]�[�ۘ[YH_H\���Z[��\�^�YZ���	؛�W�[	Έ	���]��[OH��۝Y�[Z[N��[ܙ�XK�\�Y��X^]�Y���X\��[��]]��Y[�Έ�ȏ��]��[OH��X��ܛ�[����L���Y[�Έ��^X[Yێ��[�\�ȏ��H�[OH���܎��PM��PN�X\��[����۝\�^�N��ȏ�H�[X�\��وY[��O���]����]��[OH�Y[�Έ���X��ܛ�[��ٙ�����ȏ���X\����\��ۘ[YH_K������\�HXY�\H��ۙϞ��]�[�ۘ[YH_O���ۙψ\�\[�[���^�YZ�ۈ��ۙϞ��]�[��]H_O���ۙϋ�������H��[ݙH��YH[�H\�K�XZ�H�\�H�X\��[�\��[[�\�[���YH�XYH��H�\�[�Y[ۙ��YH[�\����\�ˏ�����[OH�X\��[�]���ȏ���ۙϒ�Y\�[X�[�����\�����ۙϏ�����H�[X�\��وY[�X[O����]����]������K�	�[\]W��^IΈ	�]�[�ܙ[Z[�\��Y	��	��X��X�	Έ	��[ܜ��Έ��]�[�ۘ[YH_I��	؛�W�[	Έ	���]��[OH��۝Y�[Z[N��[ܙ�XK�\�Y��X^]�Y���X\��[��]]��Y[�Έ�ȏ��]��[OH��X��ܛ�[����L���Y[�Έ��^X[Yێ��[�\�ȏ��H�[OH���܎��PM��PN�X\��[����۝\�^�N��ȏ�H�[X�\��وY[��O���]����]��[OH�Y[�Έ���X��ܛ�[��ٙ�����ȏ������\��ۘ[YH_K�����]ZX���[Z[�\�H��ۙϞ��]�[�ۘ[YH_O���ۙψ\���ۙϝ�[ܜ������ۙϋ�������H����ܝ�\���YZ[��[�H\�K���\�������[OH�X\��[�]���ȏ���ۙϒ�Y\�[X�[�ˏ���ۙϏ�����H�[X�\��وY[�X[O����]����]������K�	�[\]W��^IΈ	�]�[��[���[�I��	��X��X�	Έ	�[��[�H�܈][�[����]�[�ۘ[YH_I��	؛�W�[	Έ	���]��[OH��۝Y�[Z[N��[ܙ�XK�\�Y��X^]�Y���X\��[��]]��Y[�Έ�ȏ��]��[OH��X��ܛ�[����L���Y[�Έ��^X[Yێ��[�\�ȏ��H�[OH���܎��PM��PN�X\��[����۝\�^�N��ȏ�H�[X�\��وY[��O���]����]��[OH�Y[�Έ���X��ܛ�[��ٙ�����ȏ���X\����\��ۘ[YH_K�����[��[�H�܈�Z[��\�و��ۙϞ��]�[�ۘ[YH_O���ۙϋ�[�\��\�[��HX]\��[�[�\���[Z]Y[��ܛ��\�[�[��\�][ۈ�H���\���������Y�[�H]�H[�H�YY�X��܈�Y�����HH]�[��H��[ݙH�X\�[HH�\��\H�\�[XZ[������[OH�X\��[�]���ȏ���ۙϒ�Y\�[X�[�����\�����ۙϏ�����H�[X�\��وY[�X[O����]����]������K�	�[\]W��^IΈ	��\��W��[��YI��	��X��X�	Έ	��[��YH����\��Wۘ[YH_K���\��ۘ[YH_I��	؛�W�[	Έ	���]��[OH��۝Y�[Z[N��[ܙ�XK�\�Y��X^]�Y���X\��[��]]��Y[�Έ�ȏ��]��[OH��X��ܛ�[����L���Y[�Έ��^X[Yێ��[�\�ȏ��H�[OH���܎��PM��PN�X\��[����۝\�^�N��ȏ�H�[X�\��وY[��O���]����]��[OH�Y[�Έ���X��ܛ�[��ٙ�����ȏ���X\����\��ۘ[YH_K�����ܙX]�]��H[�H]�H�Y[�\��YۙY���ۙϞ���\��Wۘ[YH_O���ۙψO�����[�\��\��HXY\�\���ۙϞ��XY\�ۘ[YH_O���ۙϋ���[�H�XX�[���]��[��YH[�H[��\�HHYY][��]Z[ˏ�����H\�ۈ�\��H\��\�H�X[ܛ��\[��H��Y��YZ�HX���[�X�[]K�ܚ\\�H�YK[��[�Z[�H���\�����H\�H^�]Y�܈�]���[���Y�\�ܛ�\������[OH�X\��[�]���ȏ���ۙϒ�Y\�[X�[�����\�����ۙϏ�����H�[X�\��وY[�X[O����]����]������K�	�[\]W��^IΈ	��\��W�YY][��ܙ[Z[�\���	��X��X�	Έ	�\�ۈ�\��HYY][���[Z[�\�H���\��Wۘ[YH_I��	؛�W�[	Έ	���]��[OH��۝Y�[Z[N��[ܙ�XK�\�Y��X^]�Y���X\��[��]]��Y[�Έ�ȏ��]��[OH��X��ܛ�[����L���Y[�Έ��^X[Yێ��[�\�ȏ��H�[OH���܎��PM��PN�X\��[����۝\�^�N��ȏ�\�ۈ�\��H�[Z[�\��O���]����]��[OH�Y[�Έ���X��ܛ�[��ٙ�����ȏ������\��ۘ[YH_K������\�H�[Z[�\�][�\���ۙϞ���\��Wۘ[YH_O���ۙψYY][��\���Z[��\�[ܜ��ˈ��YH�\\�Y[��XYH��\�[��������YH[�H\�K���\�������[OH�X\��[�]���ȏ���ۙϒ�Y\�[X�[�ˏ���ۙϏ����]����]������K�	�[\]W��^IΈ	�[�X�]�W��\��[����	��X��X�	Έ	����\��ۘ[YH_K�HZ\��[�H]H�[X�\��وY[���	؛�W�[	Έ	���]��[OH��۝Y�[Z[N��[ܙ�XK�\�Y��X^]�Y���X\��[��]]��Y[�Έ�ȏ��]��[OH��X��ܛ�[����L���Y[�Έ��^X[Yێ��[�\�ȏ��H�[OH���܎��PM��PN�X\��[����۝\�^�N��ȏ�H�[X�\��وY[��O���]����]��[OH�Y[�Έ���X��ܛ�[��ٙ�����ȏ���X\����\��ۘ[YH_K������H]�H��X�Y]\��Y[�H�[H�[��H�H\��ۛ�X�Y�Y�H�[�[\�[�X[�H\�X�[ۜ�[��H[�\��[�]�������]�H�[�[�H�ۛ��H[�\����\��]�H���ܙ��[�X��][�K�H�[X�\��وY[�\�\�H�[�]�\�[�H\�H�XYH��KY[��Y�K������Y�\�H\�[�][����[��ۈ]�H�[��\ܝ[�H�]܈Y�[�H��[Z�H��X�ۛ�X��[\H�\H�\�[XZ[����\��\�K���Y�[Y[�H�\����\���������[OH�X\��[�]���ȏ���ۙϖ[�H\�H��[ۙK���\�����ۙϏ�����H�[X�\��وY[�X[O����]����]��[OH��X��ܛ�[����L���Y[�ΈM\�^X[Yێ��[�\�ȏ���[OH���܎��N�Q��X\��[����۝\�^�N�L�ȏ��Y\�[X�[�����\������]����]������K�B���܈\�]H[�[\]\΂�ؚ�ܙX]YH[XZ[[\]K�ؚ�X�˙�]�ܗ�ܙX]J�[\]W��^O]\�]V��[\]W��^I�K�Y�][�^	��X��X�	Έ\�]V���X��X�	�K�	؛�W�[	Έ\�]V�؛�W�[	�K�B�
B��]\�H	�ܙX]Y	�Y�ܙX]Y[�H	�[�XYH^\���[����]�ܚ]J����]\�N��ؚ�H�B