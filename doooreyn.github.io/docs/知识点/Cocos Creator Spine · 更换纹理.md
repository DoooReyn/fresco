# Creator Spine 更换纹理

```ts
    /**
     * spine attachment 更换图片
     * @param skt 骨骼动画
     * @param slot slot名称
     * @param att attachment名称
     * @param texture 需要更换的图
     */
    changeAttachmentTexture(
        skt: sp.Skeleton,
        slot: string,
        att: string,
        texture: cc.Texture2D
    ) {
        let attachment: sp.spine.Attachment = skt.getAttachment(slot, att);

        if (!attachment) return;

        let spTexture = new sp["SkeletonTexture"]();
        spTexture.setRealTexture(texture);

        let page = new sp.spine.TextureAtlasPage();
        page.name = texture.name;
        page.uWrap = sp.spine.TextureWrap.ClampToEdge;
        page.vWrap = sp.spine.TextureWrap.ClampToEdge;
        page.texture = spTexture;
        page.texture.setWraps(page.uWrap, page.vWrap);
        page.width = texture.width;
        page.height = texture.height;

        let region = new sp.spine.TextureAtlasRegion();
        region.page = page;
        region.width = texture.width;
        region.height = texture.height;
        region.originalWidth = texture.width;
        region.originalHeight = texture.height;
        region.rotate = false;
        region.u = 0;
        region.v = 0;
        region.u2 = 1;
        region.v2 = 1;
        region.texture = spTexture;

        attachment["region"] = region;
        attachment["setRegion"](region);
        attachment["height"] = texture.height;
        attachment["width"] = texture.width;
        attachment["updateOffset"]();
    }
```
