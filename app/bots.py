import os, asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from .config import settings
from . import db

main_bot = Bot(settings.main_bot_token)
kyc_bot = Bot(settings.kyc_bot_token)
main_dp = Dispatcher(storage=MemoryStorage())
kyc_dp = Dispatcher(storage=MemoryStorage())

class KycForm(StatesGroup):
    full_name=State(); phone=State(); address=State(); purpose=State(); details=State(); id_image=State(); selfie=State(); confirm=State()

class OpForm(StatesGroup):
    deposit_amount=State(); deposit_proof=State(); withdraw_amount=State(); withdraw_wallet=State(); ticket=State()

def main_menu(active=False):
    rows=[]
    if active:
        rows += [[KeyboardButton(text='💰 إيداع'), KeyboardButton(text='🏧 سحب')],[KeyboardButton(text='📊 رصيدي'), KeyboardButton(text='📜 سجل العمليات')]]
    rows += [[KeyboardButton(text='🪪 توثيق الحساب')],[KeyboardButton(text='🎧 الدعم'), KeyboardButton(text='📞 واتساب')]]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def kyc_start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🚀 بدء التوثيق', callback_data='kyc_start')]])

async def notify_admins(text):
    for aid in settings.admin_id_list:
        try: await main_bot.send_message(aid, text)
        except Exception: pass

@main_dp.message(CommandStart())
async def main_start(m:Message):
    db.ensure_user(m.from_user.id, m.from_user.username or '', m.from_user.full_name or '')
    u=db.user(m.from_user.id)
    if u and u['is_active']:
        await m.answer(f"🔐 مرحباً بك في {settings.brand_name}\nحسابك مفعّل ويمكنك استخدام الخدمات.", reply_markup=main_menu(True))
    else:
        kb=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🪪 توثيق الحساب', url=f'https://t.me/{(await kyc_bot.me()).username}')],
            [InlineKeyboardButton(text='📞 واتساب', url=settings.whatsapp_url)]])
        await m.answer("🔒 مرحباً بك!\n\nعذراً، لا يمكنك استخدام البوت حتى يتم تفعيل حسابك.\nيرجى توثيق الحساب للمتابعة.", reply_markup=kb)

@main_dp.message(F.text=='🪪 توثيق الحساب')
async def go_kyc(m:Message):
    await m.answer('اضغط لفتح بوت التوثيق:', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='فتح التوثيق', url=f'https://t.me/{(await kyc_bot.me()).username}')]]))

@main_dp.message(F.text=='📞 واتساب')
async def wa(m:Message): await m.answer(settings.whatsapp_url)

@main_dp.message(F.text=='📊 رصيدي')
async def balance(m:Message):
    u=db.user(m.from_user.id); await m.answer(f"رصيدك الحالي: {u['balance_usdt'] if u else 0} USDT\nمستواك: {u['level'] if u else 'عادي'}")

@main_dp.message(F.text=='💰 إيداع')
async def dep(m:Message, state:FSMContext):
    u=db.user(m.from_user.id)
    if not u or not u['is_active']: return await m.answer('يجب توثيق الحساب أولاً.')
    await state.set_state(OpForm.deposit_amount); await m.answer('أدخل مبلغ الإيداع USDT:')

@main_dp.message(OpForm.deposit_amount)
async def dep_amount(m:Message, state:FSMContext):
    try: amount=float(m.text.replace(',','.'))
    except: return await m.answer('اكتب مبلغ صحيح.')
    await state.update_data(amount=amount)
    await state.set_state(OpForm.deposit_proof)
    await m.answer('أرسل صورة إثبات التحويل. سيتم مراجعتها من الإدارة.')

@main_dp.message(OpForm.deposit_proof, F.photo)
async def dep_proof(m:Message, state:FSMContext):
    data=await state.get_data(); amount=data['amount']
    os.makedirs(settings.upload_dir, exist_ok=True)
    path=os.path.join(settings.upload_dir, f"deposit_{m.from_user.id}_{m.message_id}.jpg")
    await main_bot.download(m.photo[-1], destination=path)
    db.create_operation(m.from_user.id,'إيداع',amount,proof=path)
    await state.clear(); await m.answer('✅ تم استلام طلب الإيداع وهو قيد المراجعة.')
    await notify_admins(f"طلب إيداع جديد من {m.from_user.id}: {amount} USDT")

@main_dp.message(F.text=='🏧 سحب')
async def wd(m:Message, state:FSMContext):
    u=db.user(m.from_user.id)
    if not u or not u['is_active']: return await m.answer('يجب توثيق الحساب أولاً.')
    await state.set_state(OpForm.withdraw_amount); await m.answer('أدخل مبلغ السحب USDT:')

@main_dp.message(OpForm.withdraw_amount)
async def wd_amount(m:Message, state:FSMContext):
    try: amount=float(m.text.replace(',','.'))
    except: return await m.answer('اكتب مبلغ صحيح.')
    await state.update_data(amount=amount); await state.set_state(OpForm.withdraw_wallet)
    await m.answer('أرسل عنوان محفظتك مع الشبكة، مثال: TRC20 - Txxxx')

@main_dp.message(OpForm.withdraw_wallet)
async def wd_wallet(m:Message, state:FSMContext):
    data=await state.get_data(); db.create_operation(m.from_user.id,'سحب',data['amount'],wallet=m.text)
    await state.clear(); await m.answer('✅ تم إنشاء طلب السحب وهو قيد المراجعة.')
    await notify_admins(f"طلب سحب جديد من {m.from_user.id}: {data['amount']} USDT\n{m.text}")

@main_dp.message(F.text=='🎧 الدعم')
async def support(m:Message, state:FSMContext):
    await state.set_state(OpForm.ticket); await m.answer('اكتب رسالتك للدعم:')
@main_dp.message(OpForm.ticket)
async def ticket(m:Message, state:FSMContext):
    db.add_ticket(m.from_user.id,m.text); await state.clear(); await m.answer('تم فتح تذكرتك بنجاح.')

@kyc_dp.message(CommandStart())
async def kyc_start_msg(m:Message):
    db.ensure_user(m.from_user.id, m.from_user.username or '', m.from_user.full_name or '')
    old=db.active_kyc(m.from_user.id)
    if old and old['status']=='قيد المراجعة': return await m.answer(f"لديك طلب قيد المراجعة: {old['request_no']}")
    if old and old['status']=='مقبول': return await m.answer('حسابك موثق بالفعل ✅')
    await m.answer(f"مرحباً بك في بوت توثيق {settings.brand_name}! 👋\nاضغط الزر أدناه لبدء عملية التوثيق.", reply_markup=kyc_start_kb())

@kyc_dp.callback_query(F.data=='kyc_start')
async def start_form(c, state:FSMContext):
    await state.set_state(KycForm.full_name); await c.message.answer('المعلومات الشخصية\n\nأدخل الاسم الرباعي الكامل:'); await c.answer()
@kyc_dp.message(KycForm.full_name)
async def k_name(m,state): await state.update_data(full_name=m.text); await state.set_state(KycForm.phone); await m.answer('رقم الهاتف اليمني، مثال 7xxxxxxxx:')
@kyc_dp.message(KycForm.phone)
async def k_phone(m,state):
    if not m.text.strip().startswith('7') or len(m.text.strip())<9: return await m.answer('الرقم غير صحيح. ابدأ بـ 7 واكتب الرقم كاملاً.')
    await state.update_data(phone=m.text.strip()); await state.set_state(KycForm.address); await m.answer('عنوان السكن بالتفصيل:')
@kyc_dp.message(KycForm.address)
async def k_addr(m,state):
    await state.update_data(address=m.text); await state.set_state(KycForm.purpose)
    await m.answer('اختر الغرض من شراء USDT:', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='الإيداع إلى منصة تداول')],[KeyboardButton(text='شراء منتجات أو خدمات')],[KeyboardButton(text='غرض شخصي')]], resize_keyboard=True, one_time_keyboard=True))
@kyc_dp.message(KycForm.purpose)
async def k_purpose(m,state):
    if m.text not in ['الإيداع إلى منصة تداول','شراء منتجات أو خدمات','غرض شخصي']: return await m.answer('اختر من الأزرار.')
    await state.update_data(purpose=m.text); await state.set_state(KycForm.details)
    msg='اكتب اسم منصة التداول:' if m.text=='الإيداع إلى منصة تداول' else ('اكتب اسم الموقع أو المتجر:' if m.text=='شراء منتجات أو خدمات' else 'اكتب الغرض الشخصي أو أرسل كلمة تخطي:')
    await m.answer(msg)
@kyc_dp.message(KycForm.details)
async def k_details(m,state):
    await state.update_data(details='' if m.text=='تخطي' else m.text); await state.set_state(KycForm.id_image); await m.answer('صورة الهوية\n\nأرسل/التقط صورة الهوية بوضوح.')
@kyc_dp.message(KycForm.id_image, F.photo)
async def k_id(m,state):
    os.makedirs(settings.upload_dir, exist_ok=True); path=os.path.join(settings.upload_dir,f"id_{m.from_user.id}_{m.message_id}.jpg")
    await kyc_bot.download(m.photo[-1], destination=path); await state.update_data(id_image=path); await state.set_state(KycForm.selfie); await m.answer('الصورة الشخصية\n\nأرسل صورة سيلفي واضحة.')
@kyc_dp.message(KycForm.selfie, F.photo)
async def k_selfie(m,state):
    path=os.path.join(settings.upload_dir,f"selfie_{m.from_user.id}_{m.message_id}.jpg")
    await kyc_bot.download(m.photo[-1], destination=path); await state.update_data(selfie_image=path); data=await state.get_data(); await state.set_state(KycForm.confirm)
    await m.answer(f"مراجعة المعلومات\n\nالاسم: {data['full_name']}\nالهاتف: {data['phone']}\nالعنوان: {data['address']}\nالغرض: {data['purpose']}\nتفاصيل: {data.get('details','')}\n\nالشروط: أتعهد أن البيانات صحيحة وأوافق على استخدامها للتحقق من الهوية.\n\nاكتب: أوافق")
@kyc_dp.message(KycForm.confirm)
async def k_confirm(m,state):
    if 'أوافق' not in m.text: return await m.answer('لإرسال الطلب اكتب: أوافق')
    data=await state.get_data(); data['telegram_id']=m.from_user.id
    no=db.create_kyc(data); await state.clear()
    await m.answer(f"✅ تم إرسال طلب التوثيق بنجاح!\nرقم الطلب: {no}\n\nحالة الطلب: قيد المراجعة\nالوقت المتوقع للمراجعة: من 5 - 30 دقيقة")
    await notify_admins(f"طلب KYC جديد: {no}\nالمستخدم: {m.from_user.id}\nراجع لوحة الإدارة.")

async def run_bots():
    await asyncio.gather(main_dp.start_polling(main_bot), kyc_dp.start_polling(kyc_bot))
