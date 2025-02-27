import pygame
import matplotlib.cm as cm
from datetime import datetime, timedelta

def render(env):
    if env.render_mode is None:
            return
    if env.screen is None:
        pygame.init()
        if env.render_mode == "human" or env.render_mode == "rgb_array":
            pygame.display.init()
            env.screen = pygame.display.set_mode(
                (env.screen_width, env.screen_height)
            )
            pygame.display.set_caption('WOFOST Simulator')
            pygame.display.set_icon(pygame.image.load(f'{env.assets}wofost_icon.png'))
    if env.clock is None:
        env.clock = pygame.time.Clock()

    env.screen.fill((255,255,255))

    obs_dict = dict(zip(env.output_vars+env.weather_vars+["DAYS"], env.state))

    """Title Text"""
    crop = env.agromanagement["CropCalendar"]["crop_name"]
    variety = env.agromanagement["CropCalendar"]["crop_variety"]
    title_font = pygame.font.Font(None, 64)  # Use default font, size 48
    title_surface = title_font.render(f"Growing {crop}: {variety}", True, (0, 0, 0))
    title_rect = title_surface.get_rect(center=(env.screen_width // 2, 1*env.screen_height/20))  
    env.screen.blit(title_surface, title_rect)

    """Day text"""
    date = env.agromanagement["SiteCalendar"]["site_start_date"] + timedelta(obs_dict["DAYS"])
    date_font = pygame.font.Font(None, 40)  # Use default font, size 48
    date_surface = date_font.render(f"Date: {date}", True, (0, 0, 0))
    date_rect = date_surface.get_rect(center=(env.screen_width // 2, 18.5*env.screen_height/20))  
    env.screen.blit(date_surface, date_rect)

    elapsed_font = pygame.font.Font(None, 36)  # Use default font, size 48
    elapsed_surface = elapsed_font.render(f"Days Elapsed: {int(obs_dict['DAYS'])}", True, (0, 0, 0))
    elapsed_rect = elapsed_surface.get_rect(center=(env.screen_width // 2, 19.5*env.screen_height/20))  
    env.screen.blit(elapsed_surface, elapsed_rect)


    """Crop State"""
    if obs_dict["DVS"] < 0:
        crop = pygame.image.load(f"{env.assets}crop_sowing.png").convert_alpha()
        crop_text = "Planted"
    elif obs_dict["DVS"] < 1:
        crop = pygame.image.load(f"{env.assets}crop_emerged.png").convert_alpha()
        crop_text = "Emerged"
    elif obs_dict["DVS"] < 2:
        crop = pygame.image.load(f"{env.assets}crop_veg.png").convert_alpha()
        crop_text = "Flowering"
    elif obs_dict["DVS"] < 3:
        crop = pygame.image.load(f"{env.assets}crop_ripe.png").convert_alpha()
        crop_text = "Ripe"
    else:
        crop = pygame.image.load(f"{env.assets}crop_dead.png").convert_alpha()
        crop_text = "Dead"
    crop_size = (300,225)
    resized_crop = pygame.transform.scale(crop, crop_size)
    
    crop_x = env.screen_width/2-crop_size[0]//2
    crop_y = 1*env.screen_height/3-crop_size[1]//2
    env.screen.blit(resized_crop, (crop_x, crop_y))

    pygame.draw.rect(
        env.screen, 
        (144, 238, 144), 
        (crop_x-2, crop_y-2, crop_size[0]+4, crop_size[1]+4), 
        5 # Thickness
    )

    """Draw font below crop"""
    font = pygame.font.Font(None, 48)  # Use default font, size 48
    text_surface = font.render(f"Crop State: {crop_text}", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(env.screen_width // 2, 1*env.screen_height/3 + crop_size[1]/2+25))  
    env.screen.blit(text_surface, text_rect)

    """Draw Harvest Icon"""
    cmap_wso = cm.get_cmap("Wistia")
    wso_val = env.ploader.normalize("WSO", obs_dict["WSO"])

    wso_size = (150, 100)
    wso = pygame.image.load(f"{env.assets}yield.png").convert_alpha()
    resized_wso = pygame.transform.scale(wso, wso_size)

    wso_color = tuple(int(c * 255) for c in cmap_wso(wso_val)[:3])

    wso_x = env.screen_width // 2 - wso_size[0]//2
    wso_y = 3*env.screen_height/4 - wso_size[1]//2

    wso_rect = pygame.Rect(wso_x-2, wso_y-2, wso_size[0]+4, wso_size[1]+4)
    pygame.draw.rect(env.screen, wso_color, wso_rect)
    pygame.draw.rect(env.screen, (0,0,0), wso_rect, 3)

    """Draw font below harvest"""
    wso_font = pygame.font.Font(None, 36)  # Use default font, size 48
    wso_surface = wso_font.render(f"Yield (kg/ha): {obs_dict['WSO']:0.0f}", True, (0, 0, 0))
    wso_text_rect = wso_surface.get_rect(center=(wso_x + wso_size[0] // 2, wso_y+wso_size[1]+15))  
    env.screen.blit(wso_surface, wso_text_rect)

    env.screen.blit(resized_wso, (wso_x, wso_y))

    """Draw Weather Information"""
    cmap_temp = cm.get_cmap("coolwarm")
    cmap_rain = cm.get_cmap("Blues")
    cmap_irrad = cm.get_cmap("hot_r")

    irrad_val = env.ploader.normalize("IRRAD", obs_dict["IRRAD"])
    rain_val = env.ploader.normalize("RAIN", obs_dict["RAIN"])
    temp_val = env.ploader.normalize("TEMP", obs_dict["TEMP"])

    weather_size = (100, 75)
    irrad = pygame.image.load(f"{env.assets}irrad.png").convert_alpha()
    resized_irrad = pygame.transform.scale(irrad, weather_size)
    rain = pygame.image.load(f"{env.assets}rain.png").convert_alpha()
    resized_rain = pygame.transform.scale(rain, weather_size)
    temp = pygame.image.load(f"{env.assets}temp.png").convert_alpha()
    resized_temp = pygame.transform.scale(temp, weather_size)

    temp_color = tuple(int(c * 255) for c in cmap_temp(temp_val)[:3])
    irrad_color = tuple(int(c * 255) for c in cmap_irrad(irrad_val)[:3])
    rain_color = tuple(int(c * 255) for c in cmap_rain(rain_val)[:3])

    irrad_x = 45
    irrad_y = env.screen_height/2-weather_size[1]//2
    temp_x = 45
    temp_y = env.screen_height/5-weather_size[1]//2
    rain_x = 45
    rain_y = 4*env.screen_height/5-weather_size[1]//2

    irrad_rect = pygame.Rect(irrad_x-2, irrad_y-2, weather_size[0]+4, weather_size[1]+4)
    temp_rect = pygame.Rect(temp_x-2, temp_y-2, weather_size[0]+4, weather_size[1]+4)
    rain_rect = pygame.Rect(rain_x-2, rain_y-2, weather_size[0]+4, weather_size[1]+4)

    pygame.draw.rect(env.screen, irrad_color, irrad_rect)
    pygame.draw.rect(env.screen, temp_color, temp_rect)
    pygame.draw.rect(env.screen, rain_color, rain_rect)

    pygame.draw.rect(env.screen, (0,0,0), irrad_rect, 3)
    pygame.draw.rect(env.screen, (0,0,0), temp_rect, 3)
    pygame.draw.rect(env.screen, (0,0,0), rain_rect, 3)

    """Draw font below weather"""
    irrad_font = pygame.font.Font(None, 36)  # Use default font, size 48
    irrad_surface = irrad_font.render(f"IRRAD: {obs_dict['IRRAD']:0.1e}", True, (0, 0, 0))
    irrad_text_rect = irrad_surface.get_rect(center=(irrad_x + weather_size[0] // 2, irrad_y+weather_size[1]+15))  
    env.screen.blit(irrad_surface, irrad_text_rect)

    rain_font = pygame.font.Font(None, 36)  # Use default font, size 48
    rain_surface = rain_font.render(f"RAIN: {obs_dict['RAIN']:0.2f}", True, (0, 0, 0))
    rain_text_rect = rain_surface.get_rect(center=(rain_x + weather_size[0] // 2, rain_y+weather_size[1]+15))  
    env.screen.blit(rain_surface, rain_text_rect)

    temp_font = pygame.font.Font(None, 36)  # Use default font, size 48
    temp_surface = temp_font.render(f"TEMP: {obs_dict['TEMP']:0.1f}", True, (0, 0, 0))
    temp_text_rect = temp_surface.get_rect(center=(temp_x + weather_size[0] // 2, temp_y+weather_size[1]+15))  
    env.screen.blit(temp_surface, temp_text_rect)

    env.screen.blit(resized_irrad, (irrad_x, irrad_y))
    env.screen.blit(resized_rain, (rain_x, rain_y))
    env.screen.blit(resized_temp, (temp_x, temp_y))

    """Draw Fertilization Information"""
    cmap_fert = cm.get_cmap("Greens")
    cmap_irrig = cm.get_cmap("Blues")

    n_val = env.ploader.normalize("TOTN", obs_dict["TOTN"])
    p_val = env.ploader.normalize("TOTP", obs_dict["TOTP"])
    k_val = env.ploader.normalize("TOTK", obs_dict["TOTK"])
    w_val = env.ploader.normalize("TOTIRRIG", obs_dict["TOTIRRIG"])

    fert_size = (100, 75)
    nitrogen = pygame.image.load(f"{env.assets}nitrogen.png").convert_alpha()
    resized_n = pygame.transform.scale(nitrogen, weather_size)
    phosphorous = pygame.image.load(f"{env.assets}phosphorous.png").convert_alpha()
    resized_p = pygame.transform.scale(phosphorous, weather_size)
    potassium = pygame.image.load(f"{env.assets}potassium.png").convert_alpha()
    resized_k = pygame.transform.scale(potassium, weather_size)
    irrig = pygame.image.load(f"{env.assets}irrigation.png").convert_alpha()
    resized_w = pygame.transform.scale(irrig, weather_size)

    n_color = tuple(int(c * 255) for c in cmap_fert(n_val)[:3])
    p_color = tuple(int(c * 255) for c in cmap_fert(p_val)[:3])
    k_color = tuple(int(c * 255) for c in cmap_fert(k_val)[:3])
    w_color = tuple(int(c * 255) for c in cmap_irrig(w_val)[:3])
    
    n_x = env.screen_width - fert_size[0] - 45
    n_y = 1*env.screen_height/8-fert_size[1]//2
    p_x = env.screen_width - fert_size[0] - 45
    p_y = 3*env.screen_height/8-fert_size[1]//2
    k_x = env.screen_width - fert_size[0] - 45
    k_y = 5*env.screen_height/8-fert_size[1]//2
    w_x = env.screen_width - fert_size[0] - 45
    w_y = 7*env.screen_height/8-fert_size[1]//2

    n_rect = pygame.Rect(n_x-2, n_y-2, fert_size[0]+4, fert_size[1]+4)
    p_rect = pygame.Rect(p_x-2, p_y-2, fert_size[0]+4, fert_size[1]+4)
    k_rect = pygame.Rect(k_x-2, k_y-2, fert_size[0]+4, fert_size[1]+4)
    w_rect = pygame.Rect(w_x-2, w_y-2, fert_size[0]+4, fert_size[1]+4)

    pygame.draw.rect(env.screen, n_color, n_rect)
    pygame.draw.rect(env.screen, p_color, p_rect)
    pygame.draw.rect(env.screen, k_color, k_rect)
    pygame.draw.rect(env.screen, w_color, w_rect)

    pygame.draw.rect(env.screen, (0,0,0), n_rect, 3)
    pygame.draw.rect(env.screen, (0,0,0), p_rect, 3)
    pygame.draw.rect(env.screen, (0,0,0), k_rect, 3)
    pygame.draw.rect(env.screen, (0,0,0), w_rect, 3)

    """Draw font below weather"""
    n_font = pygame.font.Font(None, 36)  # Use default font, size 48
    n_surface = n_font.render(f"N (kg/ha): {obs_dict['TOTN']:0.0f}", True, (0, 0, 0))
    n_text_rect = n_surface.get_rect(center=(n_x + fert_size[0] // 2, n_y+fert_size[1]+15))  
    env.screen.blit(n_surface, n_text_rect)

    p_font = pygame.font.Font(None, 36)  # Use default font, size 48
    p_surface = p_font.render(f"P (kg/ha): {obs_dict['TOTP']:0.0f}", True, (0, 0, 0))
    p_text_rect = p_surface.get_rect(center=(p_x + fert_size[0] // 2, p_y+fert_size[1]+15))  
    env.screen.blit(p_surface, p_text_rect)

    k_font = pygame.font.Font(None, 36)  # Use default font, size 48
    k_surface = k_font.render(f"K (kg/ha): {obs_dict['TOTK']:0.0f}", True, (0, 0, 0))
    k_text_rect = k_surface.get_rect(center=(k_x + fert_size[0] // 2, k_y+fert_size[1]+15))  
    env.screen.blit(k_surface, k_text_rect)

    w_font = pygame.font.Font(None, 36)  # Use default font, size 48
    w_surface = w_font.render(f"Water (cm/ha): {obs_dict['TOTIRRIG']:0.0f}", True, (0, 0, 0))
    w_text_rect = w_surface.get_rect(center=(w_x + fert_size[0] // 2, w_y+fert_size[1]+15))  
    env.screen.blit(w_surface, w_text_rect)

    env.screen.blit(resized_n, (n_x, n_y))
    env.screen.blit(resized_p, (p_x, p_y))
    env.screen.blit(resized_k, (k_x, k_y))
    env.screen.blit(resized_w, (w_x, w_y))

    if env.render_mode == "human":
        pygame.event.pump()
        env.clock.tick(env.render_fps)
        pygame.display.flip()
    if env.render_mode == "rgb_array":
        pygame.event.pump()
        env.clock.tick(env.render_fps)
        pygame.display.flip()
        return pygame.surfarray.array3d(pygame.display.get_surface())