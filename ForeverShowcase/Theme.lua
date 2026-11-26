-- Stagekeeper controls adapted from Forever UI 2.0.0-preview.3's native helper.
local API = ForeverShowcase
local ui = { media = 'Interface/AddOns/ForeverShowcase/Media/' }
API.Theme = ui
function ui.Label(parent, text, size, x, y, width, height, light)
    local label = parent:CreateFontString(nil, 'OVERLAY')
    label:SetFont('Fonts/FRIZQT__.TTF', size, '')
    label:SetTextColor(light and .98 or .20, light and .93 or .12, light and .79 or .07)
    label:SetShadowColor(0, 0, 0, 0)
    label:SetShadowOffset(0, 0)
    label:SetPoint('TOPLEFT', x, -y)
    label:SetSize(width, height)
    label:SetJustifyH('LEFT'); label:SetJustifyV('TOP')
    label:SetText(text)
    return label
end
function ui.Button(parent, label, width, height, kind)
    local b = CreateFrame('Button', nil, parent)
    b:SetSize(width, height)
    local pieces, cap = {}, math.min(16, width / 2)
    -- Three-slice caps preserve the brass corners at different control widths.
    for i, p in ipairs({ {0,48,cap,0}, {48,464,width-2*cap,cap}, {464,512,cap,width-cap} }) do
        if p[3] > 0 then
            local t = b:CreateTexture(nil, 'BACKGROUND')
            t:SetTexture(ui.media .. 'StagekeeperButton')
            t:SetTexCoord(p[1]/512, p[2]/512, 0, 1)
            t:SetSize(p[3], height); t:SetPoint('TOPLEFT', p[4], 0)
            pieces[#pieces+1] = t
        end
    end
    local text = ui.Label(b, label, height <= 28 and 12 or 14, 10, 5, width-20, height-10, true)
    text:SetJustifyH('CENTER'); text:SetJustifyV('MIDDLE')
    b:SetFontString(text)
    local function paint(self)
        local enabled = self:IsEnabled()
        local brightness = not enabled and .45 or self.pressed and .65 or self.hover and 1 or self.selected and 1 or .80
        for _, t in ipairs(pieces) do
            t:SetVertexColor(brightness, brightness, brightness)
            t:SetAlpha(kind == 'row' and not self.selected and not self.hover and 0 or 1)
        end
        if kind == 'row' and not self.selected and not self.hover and not self.dark then
            text:SetTextColor(.20, .12, .07)
        else text:SetTextColor(.98, .93, .79, enabled and 1 or .65) end
    end
    function b:SetSelected(value) self.selected=value; paint(self) end
    b:SetScript('OnMouseDown', function(self) self.pressed=true; paint(self) end)
    b:SetScript('OnMouseUp', function(self) self.pressed=false; paint(self) end)
    b:SetScript('OnHide', function(self) self.pressed=false; self.hover=false; paint(self) end)
    b:SetScript('OnEnter', function(self)
        self.hover=true; paint(self)
        if self.tip and GameTooltip then
            GameTooltip:SetOwner(self, 'ANCHOR_RIGHT'); GameTooltip:SetText(self.tip, 1, .93, .79, 1, true); GameTooltip:Show()
        end
    end)
    b:SetScript('OnLeave', function(self) self.hover=false; paint(self); if GameTooltip then GameTooltip:Hide() end end)
    b:SetScript('OnEnable', paint); b:SetScript('OnDisable', paint)
    paint(b)
    return b
end

-- Small working windows share the toolbar's wood, brass and live controls.
function ui.CompactWindow(name, title, width, height)
    local w=CreateFrame('Frame',name,UIParent)
    w:SetSize(width,height); w:SetPoint('CENTER'); w:SetFrameStrata('TOOLTIP'); w:SetFrameLevel(300)
    w:SetToplevel(true); w:EnableMouse(true); w:SetMovable(true); w:SetClampedToScreen(true)
    local rim=w:CreateTexture(nil,'BACKGROUND'); rim:SetAllPoints(); rim:SetColorTexture(.48,.34,.16,1)
    local fill=w:CreateTexture(nil,'BORDER'); fill:SetPoint('TOPLEFT',2,-2); fill:SetSize(width-4,height-4); fill:SetColorTexture(.12,.075,.045,1)
    local bar=w:CreateTexture(nil,'ARTWORK'); bar:SetPoint('TOPLEFT',3,-3); bar:SetSize(width-6,48)
    bar:SetTexture(ui.media..'StagekeeperShell'); bar:SetTexCoord(.025,.975,.822,.932)
    w.title=ui.Label(w,title,18,18,16,width-78,26,true)
    local drag=CreateFrame('Frame',nil,w); drag:SetPoint('TOPLEFT',4,-4); drag:SetSize(width-60,44)
    drag:EnableMouse(true); drag:RegisterForDrag('LeftButton')
    drag:SetScript('OnDragStart',function() w:Raise(); w:StartMoving() end)
    drag:SetScript('OnDragStop',function() w:StopMovingOrSizing() end)
    local close=ui.Button(w,'X',30,28); close:SetPoint('TOPRIGHT',-12,-12)
    close:SetScript('OnClick',function() w:Hide() end)
    table.insert(UISpecialFrames,name)
    w:SetScript('OnShow',function(self)
        self:SetScale(math.max(.1,math.min(1,(UIParent:GetWidth()-24)/width,(UIParent:GetHeight()-24)/height)))
        self:Raise()
    end)
    w:SetScript('OnHide',function(self) self:StopMovingOrSizing() end)
    function w:Button(label,x,y,bw,fn)
        local b=ui.Button(self,label,bw,30); b:SetPoint('TOPLEFT',x,-y); b:SetScript('OnClick',fn); return b
    end
    w:Hide(); return w
end
