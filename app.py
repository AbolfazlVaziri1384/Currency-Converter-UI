import streamlit as st
import requests
from cachetools import cached, TTLCache
from datetime import datetime
import time

# تنظیمات صفحه
st.set_page_config(
    page_title="💰 Currency Converter",
    page_icon="💱",
    layout="wide"
)

# کش برای ذخیره نرخ ارز (30 دقیقه)
ttl_cache = TTLCache(maxsize=100, ttl=1800)

# لیست ارزهای معتبر
CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY",
    "INR", "BRL", "RUB", "KRW", "MXN", "IDR", "TRY", "SAR",
    "AED", "THB", "VND", "EGP", "IRR"
]

@cached(ttl_cache)
def get_exchange_rate(base_currency, target_currency):
    """دریافت نرخ تبدیل ارز از API"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data['rates'][target_currency]
    except:
        return None

def convert_currency(amount, exchange_rate):
    """تبدیل مقدار ارز"""
    try:
        return round(amount * exchange_rate, 2)
    except:
        return None

def main():
    # هدر برنامه
    st.title("💰 Currency Converter")
    st.markdown("---")
    
    # ایجاد دو ستون برای布局 بهتر
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # بخش ورودی کاربر
        st.subheader("💱 Conversion Details")
        
        # انتخاب ارزها
        col11, col12 = st.columns(2)
        with col11:
            base_currency = st.selectbox(
                "From Currency",
                options=CURRENCIES,
                index=0,
                help="Select the currency you want to convert from"
            )
        
        with col12:
            target_currency = st.selectbox(
                "To Currency",
                options=CURRENCIES,
                index=1,
                help="Select the currency you want to convert to"
            )
        
        # ورودی مقدار
        amount = st.number_input(
            "Amount",
            min_value=0.01,
            value=100.0,
            step=1.0,
            help="Enter the amount you want to convert"
        )
        
        # دکمه تبدیل
        convert_button = st.button("🚀 Convert", type="primary", use_container_width=True)
    
    with col2:
        # اطلاعات جانبی
        st.subheader("ℹ️ Information")
        st.info("""
        **Features:**
        - Real-time exchange rates
        - 30-minute cache
        - Support for 20+ currencies
        - Instant conversion
        """)
        
        st.warning("""
        **Note:**
        Rates are updated every 30 minutes.
        For real-time rates, refresh the page.
        """)
    
    # انجام تبدیل وقتی دکمه زده شد
    if convert_button:
        if base_currency == target_currency:
            st.error("❌ Base and target currencies cannot be the same!")
            return
        
        with st.spinner("🔍 Fetching exchange rate..."):
            # شبیه‌سازی delay برای UX بهتر
            time.sleep(0.5)
            
            exchange_rate = get_exchange_rate(base_currency, target_currency)
            
            if exchange_rate is None:
                st.error("❌ Failed to fetch exchange rate. Please try again later.")
                return
            
            result = convert_currency(amount, exchange_rate)
            
            if result is not None:
                # نمایش نتیجه
                st.success("✅ Conversion Successful!")
                
                # کارت نتیجه
                st.markdown("---")
                col_result1, col_result2, col_result3 = st.columns(3)
                
                with col_result1:
                    st.metric(
                        label=f"Amount in {base_currency}",
                        value=f"{amount:,.2f}",
                        delta=None
                    )
                
                with col_result2:
                    st.metric(
                        label="Exchange Rate",
                        value=f"{exchange_rate:.4f}",
                        delta=None
                    )
                
                with col_result3:
                    st.metric(
                        label=f"Amount in {target_currency}",
                        value=f"{result:,.2f}",
                        delta=None
                    )
                
                # اطلاعات اضافی
                st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # نمایش نرخ‌های دیگر
                st.markdown("---")
                st.subheader("📊 Other Popular Rates")
                
                popular_currencies = ["EUR", "GBP", "JPY", "CAD"]
                cols = st.columns(len(popular_currencies))
                
                for i, currency in enumerate(popular_currencies):
                    if currency != base_currency:
                        rate = get_exchange_rate(base_currency, currency)
                        if rate:
                            with cols[i]:
                                st.metric(
                                    label=f"1 {base_currency} to {currency}",
                                    value=f"{rate:.3f}"
                                )
            else:
                st.error("❌ Conversion failed. Please check your inputs.")

    # تاریخچه تبدیل‌ها (با session state)
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if convert_button and result is not None:
        # اضافه کردن به تاریخچه
        conversion = {
            'date': datetime.now().strftime("%H:%M:%S"),
            'from': f"{amount} {base_currency}",
            'to': f"{result} {target_currency}",
            'rate': exchange_rate
        }
        st.session_state.history.insert(0, conversion)
        
        # محدود کردن تاریخچه به 5 مورد آخر
        if len(st.session_state.history) > 5:
            st.session_state.history = st.session_state.history[:5]
    
    # نمایش تاریخچه
    if st.session_state.history:
        st.markdown("---")
        st.subheader("📋 Recent Conversions")
        
        for i, conv in enumerate(st.session_state.history):
            col_hist1, col_hist2, col_hist3 = st.columns([1, 2, 1])
            with col_hist1:
                st.write(f"**{conv['date']}**")
            with col_hist2:
                st.write(f"{conv['from']} → {conv['to']}")
            with col_hist3:
                st.write(f"Rate: {conv['rate']:.4f}")

# اجرای برنامه
if __name__ == "__main__":
    main()