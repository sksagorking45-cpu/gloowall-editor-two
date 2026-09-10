import streamlit as st
import UnityPy
import io
from PIL import Image

# ওয়েবসাইটের ডিজাইন
st.set_page_config(page_title="Gloo Wall Texture Replacer", page_icon="🎮")
st.title("🎮 Gloo Wall Texture Replacer")
st.write("যেকোনো অরিজিনাল গেম ফাইল এবং আপনার পিএনজি (PNG) ছবি আপলোড করে এক ক্লিকেই মডিফাই করে নিন!")

st.markdown("### ১. অরিজিনাল গেম ফাইল আপলোড করুন:")
bundle_file = st.file_uploader("AssetBundle ফাইলটি নির্বাচন করুন", type=None)

st.markdown("### ২. নতুন গ্লু-ওয়াল টেক্সচার ছবি (PNG) আপলোড করুন:")
img_file = st.file_uploader("PNG ছবিটি নির্বাচন করুন", type=['png', 'jpg', 'jpeg'])

if bundle_file and img_file:
    if st.button("🚀 টেক্সচার পরিবর্তন করুন"):
        with st.spinner("প্রসেসিং হচ্ছে... দয়া করে অপেক্ষা করুন। (ফাইলের সাইজ অনুযায়ী একটু সময় লাগতে পারে)"):
            try:
                # ফাইল লোড করা
                bundle_data = bundle_file.read()
                env = UnityPy.load(bundle_data)
                img = Image.open(img_file)
                
                TARGET_PATH_ID = -5585630928333388206
                TARGET_NAME = "IceWall_Bunker_New_CSRank34_D"
                modified = False
                
                # টেক্সচার রিপ্লেস করা
                for obj in env.objects:
                    if obj.type.name == "Texture2D" and obj.path_id == TARGET_PATH_ID:
                        data = obj.read()
                        data.image = img
                        data.name = TARGET_NAME
                        data.save()
                        modified = True
                        break
                
                if modified:
                    # LZMA কম্প্রেশন
                    out_file = io.BytesIO()
                    out_file.write(env.file.save(packer="lzma"))
                    out_file.seek(0)
                    
                    st.success("✅ কাজ সফলভাবে শেষ হয়েছে! নিচের বাটন থেকে ফাইলটি ডাউনলোড করুন।")
                    st.download_button(
                        label="📥 ডাউনলোড মডিফাইড ফাইল",
                        data=out_file,
                        file_name="modified_gloowall.unity3d",
                        mime="application/octet-stream"
                    )
                else:
                    st.error("❌ সতর্কীকরণ: ফাইলে নির্দিষ্ট Path ID পাওয়া যায়নি! সঠিক ফাইল আপলোড করেছেন কিনা যাচাই করুন।")
                    
            except Exception as e:
                st.error(f"❌ কোনো সমস্যা হয়েছে: {e}")
