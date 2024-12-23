import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

# .env dosyasındaki token'ı yüklemek
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Botu başlatma
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guild_messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Log kanal ID'si
log_channel_id = 1320091379753422920  # Logları göndereceğiniz kanalın ID'si

# Komutlar için bir uyarı sayacı
warnings = {}

# Sunucuya giriş yapıldığında bilgi verme
@bot.event
async def on_ready():
    print(f'{bot.user} botu başarıyla giriş yaptı!')
    log_message.start()
    await update_bot_status()

# Sunuculara göre botun durumunu güncelleme
async def update_bot_status():
    server_count = len(bot.guilds)  # Botun bulunduğu sunucu sayısı
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"{server_count} Adet Sunucuyu")
    await bot.change_presence(activity=activity)

# Loglama işlevini başlatıyoruz
@tasks.loop(seconds=60)
async def log_message():
    channel = bot.get_channel(log_channel_id)
    if channel:
        await channel.send("Log mesajı - Her 60 saniyede bir log gönderildi.")
    else:
        print("Log kanalı bulunamadı!")

# Yardım komutunu devre dışı bırakıyoruz
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Bu komut bulunamadı.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komutu kullanmak için yeterli izinleriniz yok.")

# Sunucu hakkında bilgi komutu
@bot.command()
async def server_info(ctx):
    """Sunucu hakkında bilgi verir."""
    server = ctx.guild
    embed = discord.Embed(title="Sunucu Bilgileri", color=discord.Color.blue())
    embed.add_field(name="Sunucu Adı", value=server.name)
    embed.add_field(name="Sunucu ID", value=server.id)
    embed.add_field(name="Üye Sayısı", value=server.member_count)
    embed.add_field(name="Sunucu Kuruluş Tarihi", value=server.created_at.strftime('%Y-%m-%d'))
    await ctx.send(embed=embed)

# Kullanıcı hakkında bilgi komutu
@bot.command()
async def user_info(ctx, user: discord.User):
    """Kullanıcı bilgilerini gösterir."""
    embed = discord.Embed(title=f"{user.name} Bilgileri", color=discord.Color.green())
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Hesap Kuruluş Tarihi", value=user.created_at.strftime('%Y-%m-%d'))
    embed.add_field(name="Sunucuya Katılma Tarihi", value=user.joined_at.strftime('%Y-%m-%d'))
    embed.set_thumbnail(url=user.avatar.url)
    await ctx.send(embed=embed)

# Kullanıcıyı kickleme komutu
@bot.command()
async def kick(ctx, user: discord.User, *, reason=None):
    """Bir kullanıcıyı sunucudan atar."""
    await user.kick(reason=reason)
    await ctx.send(f"{user} atıldı. Sebep: {reason}")

# Kullanıcıyı banlama komutu
@bot.command()
async def ban(ctx, user: discord.User, *, reason=None):
    """Bir kullanıcıyı yasaklar."""
    await user.ban(reason=reason)
    await ctx.send(f"{user} yasaklandı. Sebep: {reason}")

# Yasaklamayı kaldırma komutu
@bot.command()
async def unban(ctx, user: discord.User):
    """Bir kullanıcının yasaklamasını kaldırır."""
    await ctx.guild.unban(user)
    await ctx.send(f"{user} yasaklaması kaldırıldı.")

# Kullanıcıya uyarı verme komutu
@bot.command()
async def warn(ctx, user: discord.User, *, reason=None):
    """Kullanıcıya uyarı verir."""
    if user.id not in warnings:
        warnings[user.id] = 1
    else:
        warnings[user.id] += 1

    await ctx.send(f"{user} kullanıcısına {warnings[user.id]}. uyarı verildi. Sebep: {reason}")

# Kullanıcıyı susturma komutu
@bot.command()
async def mute(ctx, user: discord.Member, *, reason=None):
    """Kullanıcıyı susturur."""
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))

    await user.add_roles(muted_role, reason=reason)
    await ctx.send(f"{user} susturuldu. Sebep: {reason}")

# Kullanıcının susturmasını kaldırma komutu
@bot.command()
async def unmute(ctx, user: discord.Member):
    """Kullanıcının susturmasını kaldırır."""
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if muted_role in user.roles:
        await user.remove_roles(muted_role)
        await ctx.send(f"{user} susturması kaldırıldı.")
    else:
        await ctx.send(f"{user} zaten susturulmamış.")

# Kullanıcıya rol verme komutu
@bot.command()
async def add_role(ctx, user: discord.Member, role_name: str):
    """Kullanıcıya belirli bir rol verir."""
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await user.add_roles(role)
        await ctx.send(f"{user} kullanıcısına {role_name} rolü verildi.")
    else:
        await ctx.send(f"{role_name} rolü bulunamadı.")

# Kullanıcıdan rol alma komutu
@bot.command()
async def remove_role(ctx, user: discord.Member, role_name: str):
    """Kullanıcıdan belirli bir rol alır."""
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await user.remove_roles(role)
        await ctx.send(f"{user} kullanıcısından {role_name} rolü alındı.")
    else:
        await ctx.send(f"{role_name} rolü bulunamadı.")

# Sunucuya yeni rol ekleme komutu
@bot.command()
async def create_role(ctx, role_name: str, color: str):
    """Sunucuya yeni bir rol ekler."""
    guild = ctx.guild
    await guild.create_role(name=role_name, color=discord.Color(int(color, 16)))
    await ctx.send(f"{role_name} rolü başarıyla oluşturuldu.")

# Rol silme komutu
@bot.command()
async def delete_role(ctx, role_name: str):
    """Sunucudan bir rol siler."""
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await role.delete()
        await ctx.send(f"{role_name} rolü silindi.")
    else:
        await ctx.send(f"{role_name} rolü bulunamadı.")

# Sunucu ayarlarını değiştirme komutu
@bot.command()
async def change_server_name(ctx, new_name: str):
    """Sunucu adını değiştirir."""
    await ctx.guild.edit(name=new_name)
    await ctx.send(f"Sunucu adı {new_name} olarak değiştirildi.")

# Sunucudan bir üyeyi atma komutu
@bot.command()
async def ban_member(ctx, user: discord.User):
    """Bir üyeyi sunucudan atar."""
    await ctx.guild.ban(user)
    await ctx.send(f"{user} sunucudan atıldı.")

# Sunucunun banlı üyelerinin listesini gösterir
@bot.command()
async def banned_users(ctx):
    """Sunucudaki banlı üyeleri listeler."""
    bans = await ctx.guild.bans()
    embed = discord.Embed(title="Banlı Üyeler", color=discord.Color.red())
    for ban_entry in bans:
        user = ban_entry.user
        embed.add_field(name=user.name, value=user.id, inline=False)
    await ctx.send(embed=embed)

# Kullanıcıların son aktivitelerini kontrol etme komutu
@bot.command()
async def last_activity(ctx, user: discord.User):
    """Kullanıcının son çevrim içi aktivitesini gösterir."""
    member = ctx.guild.get_member(user.id)
    if member:
        last_message = member.activities
        await ctx.send(f"{user.name}'ın son aktivitesi: {last_message}")
    else:
        await ctx.send(f"{user.name} sunucuda aktif değil.")

# Tüm üyeleri listeleme komutu
@bot.command()
async def list_members(ctx):
    """Sunucudaki tüm üyeleri listeler."""
    members = ctx.guild.members
    member_names = [member.name for member in members]
    await ctx.send(f"Sunucudaki üyeler: {', '.join(member_names)}")

# Sunucuya hoş geldin mesajı atma
@bot.command()
async def welcome_message(ctx):
    """Sunucuya hoş geldin mesajı gönderir."""
    welcome_channel = discord.utils.get(ctx.guild.text_channels, name='genel')  # Kanal adı değiştirilebilir
    if welcome_channel:
        await welcome_channel.send("Herkese merhaba! Hoş geldiniz!")
    else:
        await ctx.send("Hoş geldin kanalı bulunamadı.")

# Botu durdurma komutu
@bot.command()
async def shutdown(ctx):
    """Botu durdurur."""
    if ctx.author.id == 1306575171477573737:  # Sadece admin ID'si ile çalışır
        await ctx.send("Bot kapanıyor...")
        await bot.close()
    else:
        await ctx.send("Bu komutu kullanmaya yetkiniz yok.")

@bot.command()
async def leave(ctx):
    """Bot belirtilen kullanıcı ID'si ile çalışırsa sunucudan çıkar."""
    # Belirli bir ID (admin ID) kontrolü yapıyoruz
    authorized_user_id = 1306575171477573737  # Bu ID'yi değiştirebilirsiniz

    if ctx.author.id == authorized_user_id:
        await ctx.send(f"{ctx.guild.name} sunucusundan çıkıyorum...")
        await ctx.guild.leave()  # Sunucudan çıkma işlemi
    else:
        await ctx.send("Bu komutu kullanmaya yetkiniz yok.")

# Botu çalıştırma
bot.run(TOKEN)