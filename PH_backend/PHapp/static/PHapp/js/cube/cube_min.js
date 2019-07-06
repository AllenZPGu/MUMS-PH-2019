function Color(a, b, c, d, e) {
    this.name = a;
    this.initial = b;
    this.hex = c;
    this.styleF = d;
    this.styleB = e
}

var W = WHITE = new Color("white", "W", "#FFF", "font-weight: bold; color: #888", "background-color: #F3F3F3; color: rgba( 0, 0, 0, 0.5 )"),
    O = ORANGE = new Color("orange", "O", "#F60", "font-weight: bold; color: #F60", "background-color: #F60; color: rgba( 255, 255, 255, 0.9 )"),
    B = BLUE = new Color("blue", "B", "#00D", "font-weight: bold; color: #00D", "background-color: #00D; color: rgba( 255, 255, 255, 0.9 )"),
    R = RED = new Color("red", "R", "#F00", "font-weight: bold; color: #F00", "background-color: #F00; color: rgba( 255, 255, 255, 0.9 )"),
    G = GREEN = new Color("green", "G", "#0A0", "font-weight: bold; color: #0A0", "background-color: #0A0; color: rgba( 255, 255, 255, 0.9 )"),
    Y = YELLOW = new Color("yellow", "Y", "#FE0", "font-weight: bold; color: #ED0", "background-color: #FE0; color: rgba( 0, 0, 0, 0.5 )"),
    A = GRAY = new Color("gray", "A", "#777", "font-weight: bold; color: #666", "background-color: #777; color: rgba(0,0,0,0.5)"),
    P = PURPLE = new Color("purple", "P", "#F0F", "font-weight: bold; color: #E0E", "background-color: #F0F; color: rgba(255, 255, 255, 0.9)"),
    COLORLESS = new Color("NA", "X", "#DDD", "color: #EEE", "color: #DDD");

var colDict = {"W":W, "O":O, "B":B, "R":R, "G":G, "Y":Y, "A":A, "P":P};

var globalColourMap = [
    [A, A, , , A, ], // 0
    [A, A, , , , ], // 1
    [A, A, A, , , ], // 2
    [A, , , , A], // 3
    [A, , , , , ], // 4
    [A, , A, , , ], // 5
    [A, , , A, A], // 6
    [A, , , A, , ], // 7
    [A, , A, A, , ], // 8
    [, A, , , A], // 9
    [, A, , , , ], // 10
    [, A, A, , , ], // 11
    [, , , , A], // 12
    [, , , , , ], // 13
    [, , A, , , ], // 14
    [, , , A, A], // 15
    [, , , A, , ], // 16
    [, , A, A, , ], // 17
    [, A, , , A, A], // 18
    [, A, , , , A], // 19
    [, A, A, , , A], // 20
    [, , , , A, A], // 21
    [, , , , , A], // 22
    [, , A, , , A], // 23
    [, , , A, A, A], // 24
    [, , , A, , A], // 25
    [, , A, A, , A] // 26
];

var cubeletPuzzleMap = [
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
    ['', '', '', '', '',''],
];

$.ajax({
    url: '/ajax/colourCube/',
    data: {},
    dataType: 'json',
    success: function (data) {
        for (var i = 0; i < data.coloured.length; i++) {
            globalColourMap[data.coloured[i].cubeletId][data.coloured[i].cubeface]=colDict[data.coloured[i].colour];
        };

        cubeletPuzzleMap = data.cubeMap;

        grandCall();

        loadingMsg = document.getElementById("loading-message");
        loadingMsg.parentNode.removeChild(loadingMsg);
    }
});

function grandCall() {
    function Cubelet(a, b, c) {
        this.cube = a;
        this.id = b || 0;
        this.setAddress(this.id);
        this.size = a.cubeletSize || 140;
        b = this.addressX * this.size;
        var d = this.addressY * this.size,
            e = this.addressZ * this.size;
        this.anchor = new THREE.Object3D;
        this.anchor.name = "anchor-" + this.id;
        this.cube ? this.cube.threeObject.add(this.anchor) : scene.add(this.anchor);
        "css" === erno.renderMode ? (a = document.createElement("div"), a.classList.add("cubelet"), a.classList.add("cubeletId-" + this.id), this.wrapper = new THREE.CSS3DObject(a)) : "svg" === erno.renderMode &&
            (this.wrapper = new THREE.Object3D, this.plastic = new THREE.Mesh(new THREE.CubeGeometry(a.cubeletSize, a.cubeletSize, a.cubeletSize), new THREE.MeshBasicMaterial({
                color: 16777215,
                vertexColors: THREE.FaceColors
            })), this.plastic.position.set(b, d, e), this.wrapper.add(this.plastic), this.wireframe = new THREE.Mesh(new THREE.CubeGeometry(a.cubeletSize, a.cubeletSize, a.cubeletSize), new THREE.MeshBasicMaterial({
                color: 52479,
                wireframe: !0
            })), this.wireframe.position.set(b, d, e), this.wrapper.add(this.wireframe));
        this.wrapper.name =
            "wrapper-" + this.id;
        this.wrapper.position.set(b, d, e);
        this.anchor.add(this.wrapper);
        a = 0;
        void 0 === c && (c = [W, O, , , G]);
        this.faces = [];
        for (b = 0; 6 > b; b++) {
            d = c[b] || COLORLESS;
            this.faces[b] = {};
            this.faces[b].id = b;
            this.faces[b].color = d;
            this.faces[b].normal = Direction.getNameById(b);
            if ("css" === erno.renderMode) {
                var f = document.createElement("div");
                f.classList.add("face");
                f.classList.add("face" + Direction.getNameById(b).capitalize());
                this.wrapper.element.appendChild(f);
                e = document.createElement("div");
                e.classList.add("wireframe");
                f.appendChild(e);
                e = document.createElement("div");
                e.classList.add("id");
                f.appendChild(e);
                var g = document.createElement("span");
                g.innerText = cubeletPuzzleMap[this.id][b];
                e.appendChild(g)
            }
            if (d === COLORLESS) "css" === erno.renderMode ? f.classList.add("faceIntroverted") : (this.plastic.geometry.faces[b].color.setHex(0), this.plastic.geometry.colorsNeedUpdate = !0);
            else if (a++, "css" === erno.renderMode) {
                f.classList.add("faceExtroverted");
                var h = document.createElement("div");
                h.classList.add("sticker");
                h.style.backgroundColor =
                    d.hex;
                f.appendChild(h);
                d = document.createElement("div");
                d.classList.add("text");
                d.innerText = b;
                this.faces[b].text = d;
                f.appendChild(d)
            } else this.plastic.geometry.faces[[3, 3, 3, 3, 3, 3][b]].color.setHex(colorNameToDecimal(d)), this.plastic.geometry.colorsNeedUpdate = !0
        }
        this.type = ["core", "center", "edge", "corner"][a];
        this.map();
        this.front.color && "white" === this.front.color.name && "center" === this.type && "css" === erno.renderMode && h.classList.add("stickerLogo");
        this.isTweening = !0;
        this.isEngagedZ = this.isEngagedY = this.isEngagedX = !1;
        this.z = this.zPrevious = this.y = this.yPrevious = this.x = this.xPrevious = 0;
        this.show();
        this.showPlastics();
        this.showIntroverts();
        this.showStickers();
        this.hideIds();
        this.hideTexts();
        this.hideWireframes();
        this.isTweening = !1;
        this.opacity = 1;
        this.radius = 0
    }
    setupTasks = window.setupTasks || [];
    setupTasks.push(function() {
        augment(Cubelet, {
            map: function() {
                this.front = this.faces[0];
                this.up = this.faces[1];
                this.right = this.faces[2];
                this.down = this.faces[3];
                this.left = this.faces[4];
                this.back = this.faces[5];
                this.colors = (this.faces[0].color ? this.faces[0].color.initial : "-") + (this.faces[1].color ? this.faces[1].color.initial : "-") + (this.faces[2].color ? this.faces[2].color.initial : "-") + (this.faces[3].color ? this.faces[3].color.initial : "-") + (this.faces[4].color ? this.faces[4].color.initial : "-") + (this.faces[5].color ?
                    this.faces[5].color.initial : "-")
            },
            setAddress: function(a) {
                this.address = a || 0;
                this.addressX = a.modulo(3).subtract(1);
                this.addressY = -1 * a.modulo(9).divide(3).roundDown().subtract(1);
                this.addressZ = -1 * a.divide(9).roundDown().subtract(1)
            },
            inspect: function(a) {
                if (void 0 !== a) return this[a].color || "!";
                var b = this;
                a = this.id;
                var c = this.address,
                    d = this.type,
                    e = function(c, a, d) {
                        c = b[c].color.name.toUpperCase();
                        void 0 !== a && void 0 !== d && (1 === a ? c = c.justifyCenter(d) : 0 === a && (c = c.justifyLeft(d)));
                        return c
                    };
                10 > a && (a = "0" + a);
                10 >
                    c && (c = "0" + c);
                // console.log("\n    ID         " + a + "\n    Type       " + d.toUpperCase() + "\n\n    Address    " + c + "\n    Address X  " + this.addressX.toSignedString() + "\n    Address Y  " + this.addressY.toSignedString() + "\n    Address Z  " + this.addressZ.toSignedString() + "\n\n    Engaged X  " + this.isEngagedX + "\n    Engaged Y  " + this.isEngagedY + "\n    Engaged Z  " + this.isEngagedZ + "\n    Tweening   " + this.isTweening + "\n\n%c 0  Front      " + e("front", 0, 7) + "%c\n%c 1  Up         " + e("up", 0, 7) + "%c\n%c 2  Right      " +
                //     e("right", 0, 7) + "%c\n%c 3  Down       " + e("down", 0, 7) + "%c\n%c 4  Left       " + e("left", 0, 7) + "%c\n%c 5  Back       " + e("back", 0, 7) + "%c\n\n              -----------  %cback%c\n            /    %cup%c     /|  %c5%c\n           /     %c1%c     / | %c" + e("back") + "%c\n          /%c" + e("up", 1, 11) + "%c/  |\n  %cleft%c    -----------   %cright%c\n   %c4%c     |           |   %c2%c\n%c" + e("left", 1, 8) + "%c |   %cfront%c   |  %c" + e("right") + "%c\n         |     %c0%c     |  /\n         |%c" + e("front", 1, 11) + "%c| /\n         |           |/\n          -----------\n               %cdown%c\n                %c3%c\n           %c" +
                //     e("down", 1, 11) + "%c\n", this.front.color.styleB, "", this.up.color.styleB, "", this.right.color.styleB, "", this.down.color.styleB, "", this.left.color.styleB, "", this.back.color.styleB, "", this.back.color.styleF, "", this.up.color.styleF, "", this.back.color.styleF, "", this.up.color.styleF, "", this.back.color.styleF, "", this.up.color.styleF, "", this.left.color.styleF, "", this.right.color.styleF, "", this.left.color.styleF, "", this.right.color.styleF, "", this.left.color.styleF, "", this.front.color.styleF, "", this.right.color.styleF,
                //     "", this.front.color.styleF, "", this.front.color.styleF, "", this.down.color.styleF, "", this.down.color.styleF, "", this.down.color.styleF, "")
            },
            hasColor: function(a) {
                var b;
                for (b = 0; 6 > b; b++)
                    if (this.faces[b].color === a) {
                        var c = b;
                        break
                    } return void 0 !== c ? "front up right down left back".split(" ")[c] : !1
            },
            hasColors: function() {
                var a = this,
                    b = !0;
                Array.prototype.slice.call(arguments).forEach(function(c) {
                    b = b && !!a.hasColor(c)
                });
                return b
            },
            rotate: function(a, b, c) {
                var d = this,
                    e = 0,
                    f = 0,
                    g = 0,
                    h = a.toUpperCase();
                this.isTweening = !0;
                "X" === h ? (d.isEngagedX = !0, e = "X" === a ? b : -b) : "Y" === h ? (d.isEngagedY = !0, f = "Y" === a ? b : -b) : "Z" === h && (d.isEngagedZ = !0, g = "Z" === a ? b : -b);
                this.x += e.round();
                this.y += f.round();
                this.z += g.round();
                a = void 0 !== this.cube ? this.cube.twistDuration : SECOND;
                b = [b.absolute().scale(0, 90, 0, a), 250].maximum();
                (new TWEEN.Tween(this.anchor.rotation)).to({
                    x: -e.degreesToRadians(),
                    y: -f.degreesToRadians(),
                    z: -g.degreesToRadians()
                }, b).easing(TWEEN.Easing.Quartic.Out).start().onComplete(function() {
                    render();
                    d.wrapper.applyMatrix(d.anchor.matrix);
                    d.anchor.rotation.set(0, 0, 0);
                    var a = d.x.divide(90).round().subtract(d.xPrevious.divide(90).round()).absolute(),
                        b = d.y.divide(90).round().subtract(d.yPrevious.divide(90).round()).absolute(),
                        e = d.z.divide(90).round().subtract(d.zPrevious.divide(90).round()).absolute();
                    // .9 <= erno.verbosity && console.log("Cublet #" + (10 > d.id ? "0" + d.id : d.id), " |  xRemaps:", a, " yRemaps:", b, " zRemaps:", e, " |  xPrev:", d.xPrevious, " x:", d.x, " |  yPrev:", d.yPrevious, " y:", d.y, " |  zPrev:", d.zPrevious, " z:", d.z);
                    if (a) {
                        for (; a--;) d.faces =
                            d.x < d.xPrevious ? [d.up, d.back, d.right, d.front, d.left, d.down] : [d.down, d.front, d.right, d.back, d.left, d.up], d.map(), void 0 !== c && (c(d.cube.cubelets.slice()), d.cube.map());
                        d.xPrevious = d.x
                    }
                    .001 > d.x.modulo(90).absolute() && (d.x = 0, d.xPrevious = d.x, d.isEngagedX = !1);
                    if (b) {
                        for (; b--;) d.faces = d.y < d.yPrevious ? [d.left, d.up, d.front, d.down, d.back, d.right] : [d.right, d.up, d.back, d.down, d.front, d.left], d.map(), void 0 !== c && (c(d.cube.cubelets.slice()), d.cube.map());
                        d.yPrevious = d.y
                    }
                    .001 > d.y.modulo(90).absolute() && (d.y = 0, d.yPrevious =
                        d.y, d.isEngagedY = !1);
                    if (e) {
                        for (; e--;) d.faces = d.z < d.zPrevious ? [d.front, d.right, d.down, d.left, d.up, d.back] : [d.front, d.left, d.up, d.right, d.down, d.back], d.map(), void 0 !== c && (c(d.cube.cubelets.slice()), d.cube.map());
                        d.zPrevious = d.z
                    }
                    .001 > d.z.modulo(90).absolute() && (d.z = 0, d.zPrevious = d.z, d.isEngagedZ = !1);
                    d.isTweening = !1
                })
            },
            show: function() {
                $(".cubeletId-" + this.id).show();
                this.showing = !0
            },
            hide: function() {
                $(".cubeletId-" + this.id).hide();
                this.showing = !1
            },
            showPlastics: function() {
                "css" === erno.renderMode ? $(".cubeletId-" +
                    this.id + " .face").removeClass("faceTransparent") : this.plastic.material.opacity = 1;
                this.showingPlastics = !0
            },
            hidePlastics: function() {
                "css" === erno.renderMode ? $(".cubeletId-" + this.id + " .face").addClass("faceTransparent") : this.plastic.material.opacity = 0;
                this.showingPlastics = !1
            },
            showExtroverts: function() {
                $(".cubeletId-" + this.id + " .faceExtroverted").show();
                this.showingExtroverts = !0
            },
            hideExtroverts: function() {
                $(".cubeletId-" + this.id + " .faceExtroverted").hide();
                this.showingExtroverts = !1
            },
            showIntroverts: function() {
                $(".cubeletId-" +
                    this.id + " .faceIntroverted").show();
                this.showingIntroverts = !0
            },
            hideIntroverts: function() {
                $(".cubeletId-" + this.id + " .faceIntroverted").hide();
                this.showingIntroverts = !1
            },
            showStickers: function() {
                "css" === erno.renderMode ? $(".cubeletId-" + this.id + " .sticker").show() : this.faces.forEach(function(a) {
                    a.sticker && (a.sticker.material.opacity = 1)
                });
                this.showingStickers = !0
            },
            hideStickers: function() {
                "css" === erno.renderMode ? $(".cubeletId-" + this.id + " .sticker").hide() : this.faces.forEach(function(a) {
                    a.sticker && (a.sticker.material.opacity =
                        0)
                });
                this.showingStickers = !1
            },
            showWireframes: function() {
                "css" === erno.renderMode ? $(".cubeletId-" + this.id + " .wireframe").show() : this.wireframe.material.opacity = 1;
                this.showingWireframes = !0
            },
            hideWireframes: function() {
                "css" === erno.renderMode ? $(".cubeletId-" + this.id + " .wireframe").hide() : this.wireframe.material.opacity = 0;
                this.showingWireframes = !1
            },
            showIds: function() {
                $(".cubeletId-" + this.id + " .id").show();
                this.showingIds = !0
            },
            hideIds: function() {
                $(".cubeletId-" + this.id + " .id").hide();
                this.showingIds = !1
            },
            showTexts: function() {
                $(".cubeletId-" +
                    this.id + " .text").show();
                this.showingTexts = !0
            },
            hideTexts: function() {
                $(".cubeletId-" + this.id + " .text").hide();
                this.showingTexts = !1
            },
            getOpacity: function() {
                return this.opacity
            },
            setOpacity: function(a, b) {
                this.opacityTween && this.opacityTween.stop();
                void 0 === a && (a = 1);
                if (a !== this.opacity) {
                    var c = this,
                        d = (a - this.opacity).absolute().scale(0, 1, 0, SECOND);
                    this.opacityTween = (new TWEEN.Tween({
                        opacity: this.opacity
                    })).to({
                        opacity: a
                    }, d).easing(TWEEN.Easing.Quadratic.InOut).onUpdate(function() {
                        $(".cubeletId-" + c.id).css("opacity",
                            this.opacity);
                        c.opacity = this.opacity
                    }).onComplete(function() {
                        b instanceof Function && b()
                    }).start()
                }
            },
            getStickersOpacity: function(a) {
                return $(".cubeletId-" + this.id + " .sticker").css("opacity")
            },
            setStickersOpacity: function(a) {
                void 0 === a && (a = .2);
                $(".cubeletId-" + this.id + " .sticker").css("opacity", a)
            },
            getRadius: function() {
                return this.radius
            },
            setRadius: function(a, b) {
                if (!1 === this.isTweening && (a = a || 0, void 0 === this.radius && (this.radius = 0), this.radius !== a)) {
                    var c = (this.radius - a).absolute().scale(0, 100, 0, SECOND),
                        d = this;
                    (new TWEEN.Tween(this.wrapper.position)).to({
                        x: this.addressX.multiply(this.size + a),
                        y: this.addressY.multiply(this.size + a),
                        z: this.addressZ.multiply(this.size + a)
                    }, c).easing(TWEEN.Easing.Quartic.Out).onComplete(function() {
                        d.radius = a;
                        b instanceof Function && b()
                    }).start()
                }
            }
        })
    });

    function Cube(a) {
        var b = this;
        this.isReady = !0;
        this.isSolving = this.isRotating = this.isShuffling = !1;
        this.taskQueue = new Queue;
        this.twistQueue = new Queue(Twist.validate);
        this.twistDuration = SECOND;
        this.shuffleMethod = this.PRESERVE_LOGO;
        this.size = 420;
        this.cubeletSize = 140;
        "css" === erno.renderMode && (this.domElement = document.createElement("div"), this.domElement.classList.add("cube"), this.threeObject = new THREE.CSS3DObject(this.domElement));
        this.threeObject.rotation.set((30).degreesToRadians(), (-30).degreesToRadians(),
            0);
        scene.add(this.threeObject);
        this.rotationDeltaX = .1;
        this.rotationDeltaY = -.05;
        this.rotationDeltaZ = 0;
        this.cubelets = [];

        globalColourMap.forEach(function(c, a) {
            b.cubelets.push(new Cubelet(b, a, c))
        });

        this.map();
        "css" === erno.renderMode && this.faces.forEach(function(c,
            a) {
            a = document.createElement("div");
            a.classList.add("faceLabel");
            a.classList.add("face" + c.face.capitalize());
            a.innerHTML = c.face.toUpperCase();
            b.domElement.appendChild(a)
        });
        this.folds = [new Fold(this.front, this.right), new Fold(this.left, this.up), new Fold(this.down, this.back)];
        "css" === erno.renderMode && (this.setText("ABCDEFGHIJKLMNOPQR", 0), this.setText("STUVWXYZ stuvwxyz ", 1), this.setText("abcedefhijklmnopqr", 2));
        a = "preset" + a.capitalize();
        !1 === this[a] instanceof Function && (a = "presetNormal");
        this[a]();
        requestAnimationFrame(b.loop);
        $(document).keypress(function(c) {
            0 === $("input:focus, textarea:focus").length && (c = String.fromCharCode(c.which), 0 <= "XxRrMmLlYyUuEeDdZzFfSsBb".indexOf(c) && b.twistQueue.add(c))
        })
    }
    setupTasks = window.setupTasks || [];
    setupTasks.push(function() {
        Cube.prototype = Object.create(Group.prototype);
        Cube.prototype.constructor = Cube;
        forceAugment(Cube, {
            map: function() {
                var a = this,
                    b;
                this.core = new Group;
                this.centers = new Group;
                this.edges = new Group;
                this.corners = new Group;
                this.crosses = new Group;
                this.cubelets.forEach(function(c, b) {
                    "core" === c.type && a.core.add(c);
                    "center" === c.type && a.centers.add(c);
                    "edge" === c.type && a.edges.add(c);
                    "corner" === c.type && a.corners.add(c);
                    "center" !== c.type && "edge" !== c.type || a.crosses.add(c)
                });
                this.left = new Slice(this.cubelets[24],
                    this.cubelets[21], this.cubelets[18], this.cubelets[15], this.cubelets[12], this.cubelets[9], this.cubelets[6], this.cubelets[3], this.cubelets[0]);
                this.left.name = "left";
                this.middle = new Slice(this.cubelets[25], this.cubelets[22], this.cubelets[19], this.cubelets[16], this.cubelets[13], this.cubelets[10], this.cubelets[7], this.cubelets[4], this.cubelets[1]);
                this.middle.name = "middle";
                this.right = new Slice(this.cubelets[2], this.cubelets[11], this.cubelets[20], this.cubelets[5], this.cubelets[14], this.cubelets[23], this.cubelets[8],
                    this.cubelets[17], this.cubelets[26]);
                this.right.name = "right";
                this.up = new Slice(this.cubelets[18], this.cubelets[19], this.cubelets[20], this.cubelets[9], this.cubelets[10], this.cubelets[11], this.cubelets[0], this.cubelets[1], this.cubelets[2]);
                this.up.name = "up";
                this.equator = new Slice(this.cubelets[21], this.cubelets[22], this.cubelets[23], this.cubelets[12], this.cubelets[13], this.cubelets[14], this.cubelets[3], this.cubelets[4], this.cubelets[5]);
                this.equator.name = "equator";
                this.down = new Slice(this.cubelets[8],
                    this.cubelets[17], this.cubelets[26], this.cubelets[7], this.cubelets[16], this.cubelets[25], this.cubelets[6], this.cubelets[15], this.cubelets[24]);
                this.down.name = "down";
                this.front = new Slice(this.cubelets[0], this.cubelets[1], this.cubelets[2], this.cubelets[3], this.cubelets[4], this.cubelets[5], this.cubelets[6], this.cubelets[7], this.cubelets[8]);
                this.front.name = "front";
                this.standing = new Slice(this.cubelets[9], this.cubelets[10], this.cubelets[11], this.cubelets[12], this.cubelets[13], this.cubelets[14], this.cubelets[15],
                    this.cubelets[16], this.cubelets[17]);
                this.standing.name = "standing";
                this.back = new Slice(this.cubelets[26], this.cubelets[23], this.cubelets[20], this.cubelets[25], this.cubelets[22], this.cubelets[19], this.cubelets[24], this.cubelets[21], this.cubelets[18]);
                this.back.name = "back";
                this.faces = [this.front, this.up, this.right, this.down, this.left, this.back];
                for (b = 0; b < this.cubelets.length; b++) this.cubelets[b].setAddress(b)
            },
            getText: function(a) {
                if (void 0 === a) return [this.folds[0].getText(), this.folds[1].getText(),
                    this.folds[2].getText()
                ];
                if (isNumeric(a) && 0 <= a && 2 >= a) return this.folds[a].getText()
            },
            setText: function(a, b) {
                void 0 === b ? (this.folds[0].setText(a), this.folds[1].setText(a), this.folds[2].setText(a)) : isNumeric(b) && 0 <= b && 2 >= b && this.folds[b].setText(a)
            },
            inspect: function(a, b) {
                a = !a;
                this.front.inspect(a, b);
                this.up.inspect(a, b);
                this.right.inspect(a, b);
                this.down.inspect(a, b);
                this.left.inspect(a, b);
                this.back.inspect(a, b)
            },
            solve: function() {
                this.isSolving = !0
            },
            isSolved: function() {
                return this.front.isSolved(FRONT) &&
                    this.up.isSolved(UP) && this.right.isSolved(RIGHT) && this.down.isSolved(DOWN) && this.left.isSolved(LEFT) && this.back.isSolved(BACK)
            },
            twist: function(a) {
                if (a instanceof Twist && !cube.isTweening()) {
                    command = a.command;
                    degrees = a.degrees;
                    // .8 <= erno.verbosity && console.log("Executing a twist command to rotate the " + a.group + " " + a.wise + " by", a.degrees, "degrees.");
                    if ("X" !== command || cube.isEngagedY() || cube.isEngagedZ()) "x" !== command || cube.isEngagedY() || cube.isEngagedZ() ? "R" !== command || cube.right.isEngagedY() || cube.right.isEngagedZ() ?
                        "r" !== command || cube.right.isEngagedY() || cube.right.isEngagedZ() ? "M" !== command || cube.middle.isEngagedY() || cube.middle.isEngagedZ() ? "m" !== command || cube.middle.isEngagedY() || cube.middle.isEngagedZ() ? "L" !== command || cube.left.isEngagedY() || cube.left.isEngagedZ() ? "l" !== command || cube.left.isEngagedY() || cube.left.isEngagedZ() || (b = function(c) {
                            cube.cubelets[18] = c[0];
                            cube.cubelets[9] = c[3];
                            cube.cubelets[0] = c[6];
                            cube.cubelets[21] = c[9];
                            cube.cubelets[3] = c[15];
                            cube.cubelets[24] = c[18];
                            cube.cubelets[15] = c[21];
                            cube.cubelets[6] =
                                c[24]
                        }, void 0 === degrees && (degrees = cube.left.getDistanceToPeg("X")), cube.left.cubelets.forEach(function(c, a) {
                            a === cube.left.cubelets.length - 1 ? c.rotate("X", degrees, b) : c.rotate("X", degrees)
                        })) : (b = function(c) {
                            cube.cubelets[18] = c[24];
                            cube.cubelets[9] = c[21];
                            cube.cubelets[0] = c[18];
                            cube.cubelets[21] = c[15];
                            cube.cubelets[3] = c[9];
                            cube.cubelets[24] = c[6];
                            cube.cubelets[15] = c[3];
                            cube.cubelets[6] = c[0]
                        }, void 0 === degrees && (degrees = cube.left.getDistanceToPeg("x")), cube.left.cubelets.forEach(function(c, a) {
                            a === cube.left.cubelets.length -
                                1 ? c.rotate("x", degrees, b) : c.rotate("x", degrees)
                        })) : (b = function(c) {
                            cube.cubelets[1] = c[7];
                            cube.cubelets[10] = c[4];
                            cube.cubelets[19] = c[1];
                            cube.cubelets[4] = c[16];
                            cube.cubelets[22] = c[10];
                            cube.cubelets[7] = c[25];
                            cube.cubelets[16] = c[22];
                            cube.cubelets[25] = c[19]
                        }, void 0 === degrees && (degrees = cube.middle.getDistanceToPeg("X")), cube.middle.cubelets.forEach(function(c, a) {
                            c.rotate("X", degrees, b)
                        })) : (b = function(c) {
                            cube.cubelets[1] = c[19];
                            cube.cubelets[10] = c[22];
                            cube.cubelets[19] = c[25];
                            cube.cubelets[4] = c[10];
                            cube.cubelets[22] =
                                c[16];
                            cube.cubelets[7] = c[1];
                            cube.cubelets[16] = c[4];
                            cube.cubelets[25] = c[7]
                        }, void 0 === degrees && (degrees = cube.middle.getDistanceToPeg("x")), cube.middle.cubelets.forEach(function(c, a) {
                            a === cube.middle.cubelets.length - 1 ? c.rotate("x", degrees, b) : c.rotate("x", degrees)
                        })) : (b = function(c) {
                                cube.cubelets[2] = c[20];
                                cube.cubelets[11] = c[23];
                                cube.cubelets[20] = c[26];
                                cube.cubelets[5] = c[11];
                                cube.cubelets[23] = c[17];
                                cube.cubelets[8] = c[2];
                                cube.cubelets[17] = c[5];
                                cube.cubelets[26] = c[8]
                            }, void 0 === degrees && (degrees = cube.right.getDistanceToPeg("x")),
                            cube.right.cubelets.forEach(function(c, a) {
                                a === cube.right.cubelets.length - 1 ? c.rotate("x", degrees, b) : c.rotate("x", degrees)
                            })) : (b = function(c) {
                            cube.cubelets[2] = c[8];
                            cube.cubelets[11] = c[5];
                            cube.cubelets[20] = c[2];
                            cube.cubelets[5] = c[17];
                            cube.cubelets[23] = c[11];
                            cube.cubelets[8] = c[26];
                            cube.cubelets[17] = c[23];
                            cube.cubelets[26] = c[20]
                        }, void 0 === degrees && (degrees = cube.right.getDistanceToPeg("X")), cube.right.cubelets.forEach(function(c, a) {
                            a === cube.right.cubelets.length - 1 ? c.rotate("X", degrees, b) : c.rotate("X", degrees)
                        })) :
                        (b = function(c) {
                            cube.cubelets = [c[18], c[19], c[20], c[9], c[10], c[11], c[0], c[1], c[2], c[21], c[22], c[23], c[12], c[13], c[14], c[3], c[4], c[5], c[24], c[25], c[26], c[15], c[16], c[17], c[6], c[7], c[8]]
                        }, void 0 === degrees && (degrees = cube.getDistanceToPeg("x")), cube.cubelets.forEach(function(c, a) {
                            a === cube.cubelets.length - 1 ? c.rotate("x", degrees, b) : c.rotate("x", degrees)
                        }));
                    else {
                        var b = function(c) {
                            cube.cubelets = [c[6], c[7], c[8], c[15], c[16], c[17], c[24], c[25], c[26], c[3], c[4], c[5], c[12], c[13], c[14], c[21], c[22], c[23], c[0], c[1],
                                c[2], c[9], c[10], c[11], c[18], c[19], c[20]
                            ]
                        };
                        void 0 === degrees && (degrees = cube.getDistanceToPeg("X"));
                        cube.cubelets.forEach(function(c, a) {
                            a === cube.cubelets.length - 1 ? c.rotate("X", degrees, b) : c.rotate("X", degrees)
                        })
                    }
                    "Y" !== command || cube.isEngagedX() || cube.isEngagedZ() ? "y" !== command || cube.isEngagedX() || cube.isEngagedZ() ? "U" !== command || cube.up.isEngagedX() || cube.up.isEngagedZ() ? "u" === command && !cube.up.isEngagedX() & !cube.up.isEngagedZ() ? (b = function(a) {
                            cube.cubelets[18] = a[20];
                            cube.cubelets[19] = a[11];
                            cube.cubelets[20] =
                                a[2];
                            cube.cubelets[9] = a[19];
                            cube.cubelets[11] = a[1];
                            cube.cubelets[0] = a[18];
                            cube.cubelets[1] = a[9];
                            cube.cubelets[2] = a[0]
                        }, void 0 === degrees && (degrees = cube.up.getDistanceToPeg("y")), cube.up.cubelets.forEach(function(a, d) {
                            d === cube.up.cubelets.length - 1 ? a.rotate("y", degrees, b) : a.rotate("y", degrees)
                        })) : "E" !== command || cube.equator.isEngagedX() || cube.equator.isEngagedZ() ? "e" !== command || cube.equator.isEngagedX() || cube.equator.isEngagedZ() ? "D" !== command || cube.down.isEngagedX() || cube.down.isEngagedZ() ? "d" !== command ||
                        cube.down.isEngagedX() || cube.down.isEngagedZ() || (b = function(a) {
                            cube.cubelets[6] = a[8];
                            cube.cubelets[7] = a[17];
                            cube.cubelets[8] = a[26];
                            cube.cubelets[15] = a[7];
                            cube.cubelets[17] = a[25];
                            cube.cubelets[24] = a[6];
                            cube.cubelets[25] = a[15];
                            cube.cubelets[26] = a[24]
                        }, void 0 === degrees && (degrees = cube.down.getDistanceToPeg("Y")), cube.down.cubelets.forEach(function(a, d) {
                            d === cube.down.cubelets.length - 1 ? a.rotate("Y", degrees, b) : a.rotate("Y", degrees)
                        })) : (b = function(a) {
                            cube.cubelets[6] = a[24];
                            cube.cubelets[7] = a[15];
                            cube.cubelets[8] =
                                a[6];
                            cube.cubelets[15] = a[25];
                            cube.cubelets[17] = a[7];
                            cube.cubelets[24] = a[26];
                            cube.cubelets[25] = a[17];
                            cube.cubelets[26] = a[8]
                        }, void 0 === degrees && (degrees = cube.down.getDistanceToPeg("y")), cube.down.cubelets.forEach(function(a, d) {
                            d === cube.down.cubelets.length - 1 ? a.rotate("y", degrees, b) : a.rotate("y", degrees)
                        })) : (b = function(a) {
                            cube.cubelets[21] = a[3];
                            cube.cubelets[22] = a[12];
                            cube.cubelets[23] = a[21];
                            cube.cubelets[12] = a[4];
                            cube.cubelets[14] = a[22];
                            cube.cubelets[3] = a[5];
                            cube.cubelets[4] = a[14];
                            cube.cubelets[5] =
                                a[23]
                        }, void 0 === degrees && (degrees = cube.equator.getDistanceToPeg("Y")), cube.equator.cubelets.forEach(function(a, d) {
                            d === cube.equator.cubelets.length - 1 ? a.rotate("Y", degrees, b) : a.rotate("Y", degrees)
                        })) : (b = function(a) {
                            cube.cubelets[21] = a[23];
                            cube.cubelets[22] = a[14];
                            cube.cubelets[23] = a[5];
                            cube.cubelets[12] = a[22];
                            cube.cubelets[14] = a[4];
                            cube.cubelets[3] = a[21];
                            cube.cubelets[4] = a[12];
                            cube.cubelets[5] = a[3]
                        }, void 0 === degrees && (degrees = cube.equator.getDistanceToPeg("y")), cube.equator.cubelets.forEach(function(a,
                            d) {
                            d === cube.equator.cubelets.length - 1 ? a.rotate("y", degrees, b) : a.rotate("y", degrees)
                        })) : (b = function(a) {
                            cube.cubelets[18] = a[0];
                            cube.cubelets[19] = a[9];
                            cube.cubelets[20] = a[18];
                            cube.cubelets[9] = a[1];
                            cube.cubelets[11] = a[19];
                            cube.cubelets[0] = a[2];
                            cube.cubelets[1] = a[11];
                            cube.cubelets[2] = a[20]
                        }, void 0 === degrees && (degrees = cube.up.getDistanceToPeg("Y")), cube.up.cubelets.forEach(function(a, d) {
                            d === cube.up.cubelets.length - 1 ? a.rotate("Y", degrees, b) : a.rotate("Y", degrees)
                        })) : (b = function(a) {
                            cube.cubelets = [a[18], a[9],
                                a[0], a[21], a[12], a[3], a[24], a[15], a[6], a[19], a[10], a[1], a[22], a[13], a[4], a[25], a[16], a[7], a[20], a[11], a[2], a[23], a[14], a[5], a[26], a[17], a[8]
                            ]
                        }, void 0 === degrees && (degrees = cube.getDistanceToPeg("y")), cube.cubelets.forEach(function(a, d) {
                            d === cube.cubelets.length - 1 ? a.rotate("y", degrees, b) : a.rotate("y", degrees)
                        })) : (b = function(c) {
                                cube.cubelets = [c[2], c[11], c[20], c[5], c[14], c[23], c[8], c[17], c[26], c[1], c[10], c[19], c[4], c[13], c[22], c[7], c[16], c[25], c[0], c[9], c[18], c[3], c[12], c[21], c[6], c[15], c[24]]
                            }, void 0 ===
                            degrees && (degrees = cube.getDistanceToPeg("Y")), cube.cubelets.forEach(function(c, a) {
                                a === cube.cubelets.length - 1 ? c.rotate("Y", degrees, b) : c.rotate("Y", degrees)
                            }));
                    "Z" !== command || cube.isEngagedX() || cube.isEngagedY() ? "z" !== command || cube.isEngagedX() || cube.isEngagedY() ? "F" !== command || cube.front.isEngagedX() || cube.front.isEngagedY() ? "f" !== command || cube.front.isEngagedX() || cube.front.isEngagedY() ? "S" !== command || cube.standing.isEngagedX() || cube.standing.isEngagedY() ? "s" !== command || cube.standing.isEngagedX() ||
                        cube.standing.isEngagedY() ? "B" !== command || cube.back.isEngagedX() || cube.back.isEngagedY() ? "b" !== command || cube.back.isEngagedX() || cube.back.isEngagedY() || (b = function(a) {
                            cube.cubelets[18] = a[24];
                            cube.cubelets[19] = a[21];
                            cube.cubelets[20] = a[18];
                            cube.cubelets[21] = a[25];
                            cube.cubelets[23] = a[19];
                            cube.cubelets[24] = a[26];
                            cube.cubelets[25] = a[23];
                            cube.cubelets[26] = a[20]
                        }, void 0 === degrees && (degrees = cube.back.getDistanceToPeg("Z")), cube.back.cubelets.forEach(function(a, d) {
                            d === cube.back.cubelets.length - 1 ? a.rotate("Z",
                                degrees, b) : a.rotate("Z", degrees)
                        })) : (b = function(a) {
                            cube.cubelets[18] = a[20];
                            cube.cubelets[19] = a[23];
                            cube.cubelets[20] = a[26];
                            cube.cubelets[21] = a[19];
                            cube.cubelets[23] = a[25];
                            cube.cubelets[24] = a[18];
                            cube.cubelets[25] = a[21];
                            cube.cubelets[26] = a[24]
                        }, void 0 === degrees && (degrees = cube.back.getDistanceToPeg("z")), cube.back.cubelets.forEach(function(a, d) {
                            d === cube.back.cubelets.length - 1 ? a.rotate("z", degrees, b) : a.rotate("z", degrees)
                        })) : (b = function(a) {
                            cube.cubelets[9] = a[11];
                            cube.cubelets[10] = a[14];
                            cube.cubelets[11] =
                                a[17];
                            cube.cubelets[12] = a[10];
                            cube.cubelets[14] = a[16];
                            cube.cubelets[15] = a[9];
                            cube.cubelets[16] = a[12];
                            cube.cubelets[17] = a[15]
                        }, void 0 === degrees && (degrees = cube.standing.getDistanceToPeg("z")), cube.standing.cubelets.forEach(function(a, d) {
                            d === cube.standing.cubelets.length - 1 ? a.rotate("z", degrees, b) : a.rotate("z", degrees)
                        })) : (b = function(a) {
                            cube.cubelets[9] = a[15];
                            cube.cubelets[10] = a[12];
                            cube.cubelets[11] = a[9];
                            cube.cubelets[12] = a[16];
                            cube.cubelets[14] = a[10];
                            cube.cubelets[15] = a[17];
                            cube.cubelets[16] = a[14];
                            cube.cubelets[17] = a[11]
                        }, void 0 === degrees && (degrees = cube.standing.getDistanceToPeg("Z")), cube.standing.cubelets.forEach(function(a, d) {
                            d === cube.standing.cubelets.length - 1 ? a.rotate("Z", degrees, b) : a.rotate("Z", degrees)
                        })) : (b = function(a) {
                            cube.cubelets[0] = a[2];
                            cube.cubelets[1] = a[5];
                            cube.cubelets[2] = a[8];
                            cube.cubelets[3] = a[1];
                            cube.cubelets[5] = a[7];
                            cube.cubelets[6] = a[0];
                            cube.cubelets[7] = a[3];
                            cube.cubelets[8] = a[6]
                        }, void 0 === degrees && (degrees = cube.front.getDistanceToPeg("z")), cube.front.cubelets.forEach(function(a,
                            d) {
                            d === cube.front.cubelets.length - 1 ? a.rotate("z", degrees, b) : a.rotate("z", degrees)
                        })) : (b = function(a) {
                            cube.cubelets[0] = a[6];
                            cube.cubelets[1] = a[3];
                            cube.cubelets[2] = a[0];
                            cube.cubelets[3] = a[7];
                            cube.cubelets[5] = a[1];
                            cube.cubelets[6] = a[8];
                            cube.cubelets[7] = a[5];
                            cube.cubelets[8] = a[2]
                        }, void 0 === degrees && (degrees = cube.front.getDistanceToPeg("Z")), cube.front.cubelets.forEach(function(a, d) {
                            d === cube.front.cubelets.length - 1 ? a.rotate("Z", degrees, b) : a.rotate("Z", degrees)
                        })) : (b = function(a) {
                            cube.cubelets = [a[2], a[5],
                                a[8], a[1], a[4], a[7], a[0], a[3], a[6], a[11], a[14], a[17], a[10], a[13], a[16], a[9], a[12], a[15], a[20], a[23], a[26], a[19], a[22], a[25], a[18], a[21], a[24]
                            ]
                        }, void 0 === degrees && (degrees = cube.getDistanceToPeg("z")), cube.cubelets.forEach(function(a, d) {
                            d === cube.cubelets.length - 1 ? a.rotate("z", degrees, b) : a.rotate("z", degrees)
                        })) : (b = function(a) {
                                cube.cubelets = [a[6], a[3], a[0], a[7], a[4], a[1], a[8], a[5], a[2], a[15], a[12], a[9], a[16], a[13], a[10], a[17], a[14], a[11], a[24], a[21], a[18], a[25], a[22], a[19], a[26], a[23], a[20]]
                            }, void 0 ===
                            degrees && (degrees = cube.getDistanceToPeg("Z")), cube.cubelets.forEach(function(a, d) {
                                d === cube.cubelets.length - 1 ? a.rotate("Z", degrees, b) : a.rotate("Z", degrees)
                            }));
                    b instanceof Function ? (a.completed = Date.now(), $("#twist").text(command).fadeIn(50, function() {
                        var a = this;
                        setTimeout(function() {
                            $(a).fadeOut(500)
                        }, 50)
                    })) : console.log("! Received a twist command (" + command + "), however some of the required Cubelets are currently engaged.")
                } else .8 <= erno.verbosity && console.log("! Received an invalid twist command: " +
                    command + ".")
            },
            showFaceLabels: function() {
                $(".faceLabel").show();
                this.showingFaceLabels = !0
            },
            hideFaceLabels: function() {
                $(".faceLabel").hide();
                this.showingFaceLabels = !1
            },
            presetBling: function() {
                var a = this;
                this.threeObject.position.y = -2E3;
                (new TWEEN.Tween(this.threeObject.position)).to({
                    y: 0
                }, 2 * SECOND).easing(TWEEN.Easing.Quartic.Out).start();
                this.threeObject.rotation.set((180).degreesToRadians(), (180).degreesToRadians(), (20).degreesToRadians());
                (new TWEEN.Tween(this.threeObject.rotation)).to({
                    x: (25).degreesToRadians(),
                    y: (-30).degreesToRadians(),
                    z: 0
                }, 3 * SECOND).easing(TWEEN.Easing.Quartic.Out).onComplete(function() {
                    a.isReady = !0;
                    updateControls()
                }).start();
                this.isReady = !1;
                this.cubelets.forEach(function(a) {
                    a.anchor.position.set(1E3 * a.addressX, 1E3 * a.addressY, 1E3 * a.addressZ);
                    var b;
                    "core" === a.type && (b = (0).random(200));
                    "center" === a.type && (b = (200).random(400));
                    "edge" === a.type && (b = (400).random(800));
                    "corner" === a.type && (b = (800).random(1E3));
                    (new TWEEN.Tween(a.anchor.position)).to({
                        x: 0,
                        y: 0,
                        z: 0
                    }, SECOND).delay(b).easing(TWEEN.Easing.Quartic.Out).onComplete(function() {
                        a.isTweening = !1
                    }).start();
                    a.isTweening = !0
                });
                updateControls(this)
            },
            presetNormal: function() {
                $("body").css("background-color", "#000");
                $("body").addClass("graydient");
                setTimeout(function() {
                    $(".cubelet").removeClass("purty")
                }, 1);
                this.show();
                this.showIntroverts();
                this.showPlastics();
                this.showStickers();
                this.hideTexts();
                this.hideWireframes();
                this.hideIds();
                this.setOpacity();
                this.setRadius();
                updateControls(this)
            },
            presetText: function(a) {
                $("body").css("background-color", "#F00");
                $("body").removeClass("graydient");
                setTimeout(function() {
                        $(".cubelet").removeClass("purty")
                    },
                    1);
                var b = this;
                setTimeout(function() {
                    b.show();
                    b.hidePlastics();
                    b.hideStickers();
                    b.hideIds();
                    b.hideIntroverts();
                    b.showTexts();
                    b.hideWireframes();
                    b.setOpacity();
                    updateControls(b)
                }, 1)
            },
            presetLogo: function() {
                var a = this;
                this.isReady = !1;
                this.presetText();
                (new TWEEN.Tween(a.threeObject.rotation)).to({
                    x: 0,
                    y: (-45).degreesToRadians(),
                    z: 0
                }, 2 * SECOND).easing(TWEEN.Easing.Quartic.Out).onComplete(function() {
                    updateControls(a);
                    a.isReady = !0;
                    a.twistQueue.add("E20d17")
                }).start()
            },
            presetTextAnimate: function() {
                var a = [(110).absolute().scale(0,
                    90, 0, cube.twistDuration), 250].maximum();
                _this = this;
                cube.shuffleMethod = cube.ALL_SLICES;
                presetHeroic(virgin);
                setTimeout(function() {
                    _this.twist("E", 20)
                }, 1);
                setTimeout(function() {
                    _this.twist("d", 20)
                }, 1 + SECOND);
                setTimeout(function() {
                    _this.twist("D", 110);
                    _this.isRotating = !0
                }, 1 + 2 * SECOND);
                setTimeout(function() {
                    _this.twist("e", 110);
                    _this.isShuffling = !0
                }, 1 + 2 * SECOND + a + 50);
                updateControls(this)
            },
            presetWireframe: function(a, b) {
                setTimeout(function() {
                    $(".cubelet").removeClass("purty")
                }, 1);
                this.showIntroverts();
                void 0 ===
                    a && (a = new Group(this.cubelets));
                void 0 === b && (b = new Group(this.cubelets), b.remove(a));
                this.show();
                b.showPlastics();
                b.showStickers();
                b.hideWireframes();
                a.hidePlastics();
                a.hideStickers();
                a.showWireframes();
                updateControls(this)
            },
            presetHighlight: function(a, b) {
                "setup" === erno.state && this.presetBling();
                void 0 === a && (a = new Group(this.cubelets));
                void 0 === b && (b = new Group(this.cubelets), b.remove(a));
                b.setOpacity(.1);
                a.setOpacity();
                updateControls(this)
            },
            presetHighlightCore: function() {
                this.presetHighlight(this.core);
                updateControls(this)
            },
            presetHighlightCenters: function() {
                this.presetHighlight(this.centers);
                updateControls(this)
            },
            presetHighlightEdges: function() {
                this.presetHighlight(this.edges);
                updateControls(this)
            },
            presetHighlightCorners: function() {
                this.presetHighlight(this.corners);
                updateControls(this)
            },
            presetHighlightWhite: function() {
                this.presetHighlight(this.hasColor(WHITE));
                updateControls(this)
            },
            presetPurty: function() {
                this.showIntroverts();
                setTimeout(function() {
                    $(".cubelet").addClass("purty")
                }, 1);
                this.threeObject.rotation.set((35.3).degreesToRadians(),
                    (-45).degreesToRadians(), 0);
                updateControls(this)
            },
            presetDemo: function() {
                var a = this,
                    b = 0,
                    c = $("#captions");
                this.taskQueue.add(function() {
                        a.rotationDeltaX = -.1;
                        a.rotationDeltaY = .15;
                        a.isRotating = !0;
                        a.presetNormal();
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    }, function() {
                        a.twistQueue.add("rdRD".multiply(6))
                    }, function() {
                        a.back.setOpacity(.2);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    }, function() {
                        a.standing.setOpacity(.2);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    }, function() {
                        a.twistQueue.add("rdRD".multiply(3))
                    }, function() {
                        a.showFaceLabels();
                        a.twistQueue.add("rdRD".multiply(3))
                    }, function() {
                        a.hideFaceLabels();
                        a.standing.setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    }, function() {
                        a.back.setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    }, function() {
                        a.down.setRadius(90);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    }, function() {
                        a.equator.setRadius(90);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    }, function() {
                        a.up.setRadius(90);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    }, function() {
                        a.twistQueue.add("rdRD".multiply(2))
                    }, function() {
                        a.back.setRadius();
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    }, function() {
                        a.standing.setRadius();
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.twistQueue.add("rdRD".multiply(2))
                    },
                    function() {
                        var b = new Group(a.cubelets),
                            c = a.hasColors(RED, YELLOW, BLUE);
                        b.remove(c);
                        b.setRadius();
                        b.setOpacity(.5);
                        c.setRadius(120);
                        c.setOpacity(1);
                        a.back.setRadius();
                        a.showIds();
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, (6).seconds())
                    },
                    function() {
                        a.twistQueue.add("rdRD".multiply(2))
                    },
                    function() {
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, (6).seconds())
                    },
                    function() {
                        a.setRadius();
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, (3).seconds())
                    },
                    function() {
                        c.text("Core").fadeIn();
                        a.presetHighlightCore();
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.showIds();
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, (2).seconds())
                    },
                    function() {
                        a.twistQueue.add("rdRD".multiply(2))
                    },
                    function() {
                        c.text("Centers");
                        a.presetHighlightCenters();
                        a.twistQueue.add("rdRD".multiply(4))
                    },
                    function() {
                        c.text("Edges");
                        a.presetHighlightEdges();
                        a.twistQueue.add("rdRD".multiply(3))
                    },
                    function() {
                        c.text("Corners");
                        a.presetHighlightCorners();
                        a.twistQueue.add("rdRD".multiply(3))
                    },
                    function() {
                        c.fadeOut();
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, (2).seconds())
                    },
                    function() {
                        a.left.setOpacity(0);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.left.hidePlastics().hideStickers().showWireframes().showIds().setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.middle.setOpacity(0);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.middle.hidePlastics().hideStickers().showWireframes().showIds().setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.right.setOpacity(0);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.right.hidePlastics().hideStickers().showWireframes().showIds().setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.twistQueue.add("rdRD".multiply(3))
                    },
                    function() {
                        a.left.setOpacity(0);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.left.hidePlastics().hideStickers().hideWireframes().hideIds().showTexts().setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.middle.setOpacity(0);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.middle.hidePlastics().hideStickers().hideWireframes().hideIds().showTexts().setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.right.setOpacity(0);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.right.hidePlastics().hideStickers().hideWireframes().hideIds().showTexts().setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.twistQueue.add("rdRD".multiply(3))
                    },
                    function() {
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, 8 * SECOND)
                    },
                    function() {
                        a.left.setOpacity(0);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.left.showPlastics().showStickers().hideTexts().setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.middle.setOpacity(0);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.middle.showPlastics().showStickers().hideTexts().setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.right.setOpacity(0);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        a.right.showPlastics().showStickers().hideTexts().setOpacity(1);
                        a.taskQueue.isReady = !1;
                        setTimeout(function() {
                            a.taskQueue.isReady = !0
                        }, SECOND)
                    },
                    function() {
                        b++;
                        // console.log("The cuber demo has completed", b, "loops.");
                        a.twistQueue.history = []
                    });
                this.taskQueue.isLooping = !0;
                updateControls(this)
            },
            presetDemoStop: function() {
                this.taskQueue.isLooping = !1;
                this.twistQueue.empty();
                this.taskQueue.empty();
                this.isRotating = !1;
                updateControls(this)
            },
            PRESERVE_LOGO: "RrLlUuDdSsBb",
            ALL_SLICES: "RrMmLlUuEeDdFfSsBb",
            EVERYTHING: "XxRrMmLlYyUuEeDdZzFfSsBb",
            loop: function() {
                cube.isRotating && (cube.threeObject.rotation.x += cube.rotationDeltaX.degreesToRadians(), cube.threeObject.rotation.y += cube.rotationDeltaY.degreesToRadians(), cube.threeObject.rotation.z += cube.rotationDeltaZ.degreesToRadians(), updateControls());
                if (cube.isReady && !cube.isTweening()) {
                    if ($("#cubeIsTweening").fadeOut(100),
                        cube.twistQueue.isReady)
                        if (0 === cube.twistQueue.future.length)
                            if ($("#cubeHasTwistsQueued").fadeOut(100), cube.isShuffling) cube.twistQueue.add(cube.shuffleMethod[cube.shuffleMethod.length.rand()]);
                            else if (cube.isSolving && window.solver) cube.isSolving = window.solver.consider(cube);
                    else {
                        if (!0 === cube.taskQueue.isReady) {
                            var a = cube.taskQueue.do();
                            a instanceof Function && a()
                        }
                    } else cube.twist(cube.twistQueue.do()), 0 < cube.twistQueue.future.length && $("#cubeHasTwistsQueued").fadeIn(100)
                } else cube.isTweening && $("#cubeIsTweening").fadeIn(100);
                requestAnimationFrame(cube.loop)
            }
        })
    });

    function Direction(a, b) {
        this.id = a;
        this.name = b.toLowerCase();
        this.initial = b.substr(0, 1).toUpperCase();
        this.neighbors = [];
        this.opposite = null
    }
    Direction.prototype.setRelationships = function(a, b, c, d, e) {
        this.neighbors = [a, b, c, d];
        this.opposite = e
    };
    Direction.getNameById = function(a) {
        return "front up right down left back".split(" ")[a]
    };
    Direction.getIdByName = function(a) {
        return {
            front: 0,
            up: 1,
            right: 2,
            down: 3,
            left: 4,
            back: 5
        } [a]
    };
    Direction.getDirectionById = function(a) {
        return [FRONT, UP, RIGHT, DOWN, LEFT, BACK][a]
    };
    Direction.getDirectionByInitial = function(a) {
        return {
            F: FRONT,
            U: UP,
            R: RIGHT,
            D: DOWN,
            L: LEFT,
            B: BACK
        } [a.toUpperCase()]
    };
    Direction.getDirectionByName = function(a) {
        return {
            front: FRONT,
            up: UP,
            right: RIGHT,
            down: DOWN,
            left: LEFT,
            back: BACK
        } [a.toLowerCase()]
    };
    Direction.prototype.getRotation = function(a, b, c) {
        void 0 === b && (b = this.neighbors[0]);
        if (b === this || b === this.opposite) return null;
        c = void 0 === c ? 1 : c.modulo(4);
        for (var d = 0; 5 > d && this.neighbors[d] !== b; d++);
        return this.neighbors[d.add(c * a).modulo(4)]
    };
    Direction.prototype.getClockwise = function(a, b) {
        return this.getRotation(1, a, b)
    };
    Direction.prototype.getAnticlockwise = function(a, b) {
        return this.getRotation(-1, a, b)
    };
    Direction.prototype.getDirection = function(a, b) {
        return this.getRotation(1, b, a.id - 1)
    };
    Direction.prototype.getUp = function(a) {
        return this.getDirection(UP, a)
    };
    Direction.prototype.getRight = function(a) {
        return this.getDirection(RIGHT, a)
    };
    Direction.prototype.getDown = function(a) {
        return this.getDirection(DOWN, a)
    };
    Direction.prototype.getLeft = function(a) {
        return this.getDirection(LEFT, a)
    };
    Direction.prototype.getOpposite = function() {
        return this.opposite
    };
    var FRONT = new Direction(0, "front"),
        UP = new Direction(1, "up"),
        RIGHT = new Direction(2, "right"),
        DOWN = new Direction(3, "down"),
        LEFT = new Direction(4, "left"),
        BACK = new Direction(5, "back");
    FRONT.setRelationships(UP, RIGHT, DOWN, LEFT, BACK);
    UP.setRelationships(BACK, RIGHT, FRONT, LEFT, DOWN);
    RIGHT.setRelationships(UP, BACK, DOWN, FRONT, LEFT);
    DOWN.setRelationships(FRONT, RIGHT, BACK, LEFT, UP);
    LEFT.setRelationships(UP, FRONT, DOWN, BACK, RIGHT);
    BACK.setRelationships(UP, LEFT, DOWN, RIGHT, FRONT);
    var erno = {
        version: 2.01311021337E7,
        verbosity: 1,
        renderMode: "css",
        state: "setup",
        stateFrames: 0,
        stateHistory: ["setup"],
        changeStateTo: function(a) {
            if (erno.state !== a) {
                // .3 <= erno.verbosity && (console.log('< Exiting  "' + erno.state + '" state at ' + erno.stateFrames + " frames."), console.log('> Entering "' + a + '" state.'));
                var b = erno.states[erno.state + "Teardown"],
                    c = erno.states[a + "Setup"];
                b instanceof Function && b();
                c instanceof Function && c();
                erno.stateHistory.push(a);
                erno.state = a;
                erno.stateFrames = 0
            }
            return !1
        },
        states: {
            setup: function() {
                // console.log("\nCuber",
                //     erno.version);
                // console.log("");
                window.help = '';
                // console.log(help);
                window.setupTasks && setupTasks.forEach(function(a) {
                    a()
                });
                setupThree();
                setupControls();
                var a = document.location.search.substr(1);
                "/" === a.charAt(a.length - 1) && (a = a.substr(0, a.length - 1));
                a = a.charAt(0).toUpperCase() + a.substr(1, a.length);

                window.cube = new Cube(a);
                updateControls();

                erno.changeStateTo("loop");

                // console.log(window.cube.cubelets[9]);
                window.cube.cubelets[9].showIds();
                // console.log(window.cube.cubelets[9]);

            },
            loop: function() {
                animate()
            }
        },
        inspect: function() {
            var a = window.performance.memory.totalJSHeapSize.divide(1048576).multiply(10).roundDown().divide(10),
                b = window.performance.memory.usedJSHeapSize.divide(1048576).multiply(10).roundDown().divide(10),
                c = window.performance.memory.usedJSHeapSize.divide(window.performance.memory.totalJSHeapSize).multiply(1E3).roundDown().divide(10);
            // console.log("");
            // console.log(now().toDate());
            // console.log("JS heap size total  ", a + " MB  (100.0%)");
            // console.log("JS heap size used   ", b + " MB  (" + c + "%)");
            // console.log("cube.twistQueue     ", cube.twistQueue.history.length + cube.twistQueue.future.length);
            // console.log("cube.taskQueue      ", cube.taskQueue.history.length + cube.taskQueue.future.length);
            // console.log("THREE.Object3D index",
            //     THREE.Object3DIdCount);
            // console.log("");
            return c
        }
    };

    function setupThree() {
        window.scene = new THREE.Scene;
        var a = document.getElementById("outer-container").offsetWidth,
            b = document.getElementById("outer-container").offsetHeight;
        window.camera = new THREE.PerspectiveCamera(45, a / b, 1, 6E3);
        camera.position.z = 1500;
        camera.tanFOV = Math.tan(Math.PI / 180 * camera.fov / 2);
        camera.oneToOne = function() {
            return -.5 / Math.tan(this.fov * Math.PI / 360) * b
        };
        camera.lookAt(scene.position);
        scene.add(camera);
        window.projector = new THREE.Projector;
        "css" === erno.renderMode ? (window.renderer = new THREE.CSS3DRenderer,
            renderer.domElement.style.position = "absolute", renderer.domElement.style.top = 0) : "svg" === erno.renderMode ? (window.renderer = new THREE.SVGRenderer, renderer.setQuality("low")) : "webgl" === erno.renderMode && (window.renderer = new THREE.WebGLRenderer({
            antialias: !0
        }), renderer.shadowMapEnabled = !0);
        renderer.setSize(a, b);
        renderer.originalHeight = b;
        document.getElementById("cube-container").appendChild(renderer.domElement);
        document.getElementById("outer-container").addEventListener("resize", onWindowResize, !1)
    }

    function setupControls() {
        window.controls = new THREE.TrackballControls(camera, renderer.domElement);
        controls.noZoom = controls.noPan = !0;
        controls.rotateSpeed = .5;
        controls.autoRotateTheta = 135;
        controls.beginAutoRotate();
        controls.mouseUpCallback = function() {
            controls.stopAutoRotate();
            controls.mouseUpCallback = !1
        }
    }

    function onWindowResize() {
        var a = document.getElementById("outer-container").offsetWidth,
            b = document.getElementById("outer-container").offsetHeight;
        camera.aspect = a / b;
        camera.fov = 360 / Math.PI * Math.atan(b / renderer.originalHeight * camera.tanFOV);
        camera.updateProjectionMatrix();
        renderer.setSize(a, b);
        render()
    }

    function animate() {
        TWEEN.update();
        if (window.controls && window.controls instanceof THREE.TrackballControls) {
            var a = camera.position.x,
                b = camera.position.y,
                c = camera.position.z,
                d = camera.rotation.x,
                e = camera.rotation.y,
                f = camera.rotation.z;
            controls.update();
            a === camera.position.x && b === camera.position.y && c === camera.position.z && d === camera.rotation.x && e === camera.rotation.y && f === camera.rotation.z || updateControls()
        }
        render()
    }

    function render() {
        renderer.render(scene, camera)
    }

    function updateControls(a) {
        $("#backgroundColorCss").val($("body").css("background-color"));
        $("#cameraFov").val(camera.fov)
    }

    function assessTrueFalseMixed(a, b) {
        0 === b ? ($(a).prop("indeterminate", !1), $(a).prop("checked", !1)) : 27 === b ? ($(a).prop("indeterminate", !1), $(a).prop("checked", !0)) : $(a).prop("indeterminate", !0)
    }

    function loop() {
        if ("complete" === document.readyState) {
            erno.stateFrames++;
            var a = erno.states[erno.state];
            a instanceof Function && a()
        }
    }
    setInterval(loop, 16);

    function Fold(a, b) {
        this.map = [a.northWest[a.face].text, a.north[a.face].text, a.northEast[a.face].text, b.northWest[b.face].text, b.north[b.face].text, b.northEast[b.face].text, a.west[a.face].text, a.origin[a.face].text, a.east[a.face].text, b.west[b.face].text, b.origin[b.face].text, b.east[b.face].text, a.southWest[a.face].text, a.south[a.face].text, a.southEast[a.face].text, b.southWest[b.face].text, b.south[b.face].text, b.southEast[b.face].text]
    }
    Fold.prototype.getText = function() {
        var a = "";
        this.map.forEach(function(b) {
            a += b.innerHTML
        });
        return a
    };
    Fold.prototype.setText = function(a) {
        var b;
        a = a.justifyLeft(18);
        for (b = 0; 18 > b; b++) this.map[b].innerHTML = a.substr(b, 1)
    };

    function Group() {
        this.cubelets = [];
        this.add(Array.prototype.slice.call(arguments))
    }
    setupTasks = window.setupTasks || [];
    setupTasks.push(function() {
        augment(Group, {
            inspect: function(a) {
                this.cubelets.forEach(function(b) {
                    b.inspect(a)
                });
                return this
            },
            add: function() {
                var a = this;
                Array.prototype.slice.call(arguments).forEach(function(b) {
                    b instanceof Group && (b = b.cubelets);
                    b instanceof Array ? a.add.apply(a, b) : a.cubelets.push(b)
                });
                return this
            },
            remove: function(a) {
                a instanceof Group && (a = a.cubelets);
                if (a instanceof Array) {
                    var b = this;
                    a.forEach(function(a) {
                        b.remove(a)
                    })
                }
                for (var c = this.cubelets.length - 1; 0 <= c; c--) this.cubelets[c] === a &&
                    this.cubelets.splice(c, 1);
                return this
            },
            isFlagged: function(a) {
                var b = 0;
                this.cubelets.forEach(function(c) {
                    b += c[a] ? 1 : 0
                });
                return b
            },
            isTweening: function() {
                return this.isFlagged("isTweening")
            },
            isEngagedX: function() {
                return this.isFlagged("isEngagedX")
            },
            isEngagedY: function() {
                return this.isFlagged("isEngagedY")
            },
            isEngagedZ: function() {
                return this.isFlagged("isEngagedZ")
            },
            isEngaged: function() {
                return this.isEngagedX() + this.isEngagedY() + this.isEngagedZ()
            },
            hasProperty: function(a, b) {
                var c = new Group;
                this.cubelets.forEach(function(d) {
                    d[a] ===
                        b && c.add(d)
                });
                return c
            },
            hasId: function(a) {
                return this.hasProperty("id", a).cubelets[0]
            },
            hasAddress: function(a) {
                return this.hasProperty("address", a).cubelets[0]
            },
            hasType: function(a) {
                return this.hasProperty("type", a)
            },
            hasColor: function(a) {
                var b = new Group;
                this.cubelets.forEach(function(c) {
                    c.hasColor(a) && b.add(c)
                });
                return b
            },
            hasColors: function() {
                var a = new Group,
                    b = Array.prototype.slice.call(arguments);
                this.cubelets.forEach(function(c) {
                    c.hasColors.apply(c, b) && a.add(c)
                });
                return a
            },
            getAverageRotation: function(a) {
                var b =
                    0;
                this.cubelets.forEach(function(c) {
                    b += c[a.toLowerCase()]
                });
                return b / this.cubelets.length
            },
            getAverageRotationX: function() {
                return this.getAverageRotation("x")
            },
            getAverageRotationY: function() {
                return this.getAverageRotation("y")
            },
            getAverageRotationZ: function() {
                return this.getAverageRotation("z")
            },
            getDistanceToPeg: function(a) {
                var b = this.getAverageRotation(a),
                    c = a.toUpperCase() === a ? "clockwise" : "anticlockwise",
                    d = b.add(90).divide(90).roundDown().multiply(90).subtract(b),
                    e = b + d;
                "anticlockwise" === c && (d -= 90,
                    0 === d && (d -= 90), e = b + d);
                // .9 <= erno.verbosity && console.log("Average rotation for this group about the " + a.toUpperCase() + " axis:", b, "\nRotation direction:", c, "\nDistance to next peg:", d, "\nTarget rotation:", e);
                return d.absolute()
            },
            isSolved: function(a) {
                if (a) {
                    var b = {},
                        c = 0;
                    a instanceof Direction && (a = a.name);
                    this.cubelets.forEach(function(d) {
                        d = d[a].color.name;
                        void 0 === b[d] ? (b[d] = 1, c++) : b[d]++
                    });
                    return 1 === c ? !0 : !1
                }
                console.warn("A face [String or Direction] argument must be specified when using Group.isSolved().");
                return !1
            },
            show: function() {
                this.cubelets.forEach(function(a) {
                    a.show()
                });
                return this
            },
            hide: function() {
                this.cubelets.forEach(function(a) {
                    a.hide()
                });
                return this
            },
            showPlastics: function() {
                this.cubelets.forEach(function(a) {
                    a.showPlastics()
                });
                return this
            },
            hidePlastics: function() {
                this.cubelets.forEach(function(a) {
                    a.hidePlastics()
                });
                return this
            },
            showExtroverts: function() {
                this.cubelets.forEach(function(a) {
                    a.showExtroverts()
                });
                return this
            },
            hideExtroverts: function() {
                this.cubelets.forEach(function(a) {
                    a.hideExtroverts()
                });
                return this
            },
            showIntroverts: function() {
                this.cubelets.forEach(function(a) {
                    a.showIntroverts()
                });
                return this
            },
            hideIntroverts: function() {
                this.cubelets.forEach(function(a) {
                    a.hideIntroverts()
                });
                return this
            },
            showStickers: function() {
                this.cubelets.forEach(function(a) {
                    a.showStickers()
                });
                return this
            },
            hideStickers: function() {
                this.cubelets.forEach(function(a) {
                    a.hideStickers()
                });
                return this
            },
            showWireframes: function() {
                this.cubelets.forEach(function(a) {
                    a.showWireframes()
                });
                return this
            },
            hideWireframes: function() {
                this.cubelets.forEach(function(a) {
                    a.hideWireframes()
                });
                return this
            },
            showIds: function() {
                this.cubelets.forEach(function(a) {
                    a.showIds()
                });
                return this
            },
            hideIds: function() {
                this.cubelets.forEach(function(a) {
                    a.hideIds()
                });
                return this
            },
            showTexts: function() {
                this.cubelets.forEach(function(a) {
                    a.showTexts()
                });
                return this
            },
            hideTexts: function() {
                this.cubelets.forEach(function(a) {
                    a.hideTexts()
                });
                return this
            },
            getOpacity: function() {
                var a = 0;
                this.cubelets.forEach(function(b) {
                    a += b.getOpacity()
                });
                return a / this.cubelets.length
            },
            setOpacity: function(a, b) {
                this.cubelets.forEach(function(c) {
                    c.setOpacity(a,
                        b)
                });
                return this
            },
            getRadius: function() {
                var a = 0;
                this.cubelets.forEach(function(b) {
                    a += b.getRadius()
                });
                return a / this.cubelets.length
            },
            setRadius: function(a, b) {
                this.cubelets.forEach(function(c) {
                    c.setRadius(a, b)
                });
                return this
            }
        })
    });

    function Queue(a) {
        void 0 !== a && a instanceof Function && (this.validate = a);
        this.history = [];
        this.future = [];
        this.isReady = !0;
        this.isLooping = !1
    }
    Queue.prototype.add = function() {
        var a = Array.prototype.slice.call(arguments),
            b = this;
        void 0 !== this.validate && this.validate instanceof Function && (a = this.validate(a));
        a instanceof Array && a.forEach(function(a) {
            b.future.push(a)
        })
    };
    Queue.prototype.empty = function() {
        this.future = []
    };
    Queue.prototype.do = function() {
        if (this.future.length) {
            var a = this.future.shift();
            this.history.push(a);
            return a
        }
        this.isLooping && (this.future = this.history.slice(), this.history = [])
    };
    Queue.prototype.undo = function() {
        if (this.history.length) {
            var a = this.history.pop();
            this.future.unshift(a);
            return a
        }
    };
    Queue.prototype.redo = function() {
        this.do()
    };

    function Slice() {
        this.cubelets = Array.prototype.slice.call(arguments);
        this.map()
    }

    setupTasks = window.setupTasks || [];
    setupTasks.push(function() {
        augment(Slice, {
            inspect: function(a, b) {
                var c = function(a) {
                        return a[b].color.name.toUpperCase().justifyCenter(9)
                    },
                    d = "";
                void 0 === b && (b = void 0 !== this.face ? this.face : "front");
                b instanceof Direction && (b = b.name);
                b !== this.face && (d = b + "s");
                // a ? console.log("\n" + this.name.capitalize().justifyLeft(10) + "%c " + this.northWest.id.toPaddedString(2) + " %c %c " + this.north.id.toPaddedString(2) + " %c %c " + this.northEast.id.toPaddedString(2) + " %c \n" + d + "\n          %c " + this.west.id.toPaddedString(2) +
                //     " %c %c " + this.origin.id.toPaddedString(2) + " %c %c " + this.east.id.toPaddedString(2) + " %c \n\n          %c " + this.southWest.id.toPaddedString(2) + " %c %c " + this.south.id.toPaddedString(2) + " %c %c " + this.southEast.id.toPaddedString(2) + " %c \n", this.northWest[b].color.styleB, "", this.north[b].color.styleB, "", this.northEast[b].color.styleB, "", this.west[b].color.styleB, "", this.origin[b].color.styleB, "", this.east[b].color.styleB, "", this.southWest[b].color.styleB, "", this.south[b].color.styleB, "", this.southEast[b].color.styleB,
                //     "") : console.log("\n          %c           %c %c           %c %c           %c \n" + this.name.capitalize().justifyLeft(10) + "%c northWest %c %c   north   %c %c northEast %c \n" + d.justifyLeft(10) + "%c " + this.northWest.id.toPaddedString(2).justifyCenter(9) + " %c %c " + this.north.id.toPaddedString(2).justifyCenter(9) + " %c %c " + this.northEast.id.toPaddedString(2).justifyCenter(9) + " %c \n          %c " + c(this.northWest) + " %c %c " + c(this.north) + " %c %c " + c(this.northEast) + " %c \n          %c           %c %c           %c %c           %c \n\n          %c           %c %c           %c %c           %c \n          %c    west   %c %c   origin  %c %c    east   %c \n          %c " +
                //     this.west.id.toPaddedString(2).justifyCenter(9) + " %c %c " + this.origin.id.toPaddedString(2).justifyCenter(9) + " %c %c " + this.east.id.toPaddedString(2).justifyCenter(9) + " %c \n          %c " + c(this.west) + " %c %c " + c(this.origin) + " %c %c " + c(this.east) + " %c \n          %c           %c %c           %c %c           %c \n\n          %c           %c %c           %c %c           %c \n          %c southWest %c %c   south   %c %c southEast %c \n          %c " + this.southWest.id.toPaddedString(2).justifyCenter(9) +
                //     " %c %c " + this.south.id.toPaddedString(2).justifyCenter(9) + " %c %c " + this.southEast.id.toPaddedString(2).justifyCenter(9) + " %c \n          %c " + c(this.southWest) + " %c %c " + c(this.south) + " %c %c " + c(this.southEast) + " %c \n          %c           %c %c           %c %c           %c\n", this.northWest[b].color.styleB, "", this.north[b].color.styleB, "", this.northEast[b].color.styleB, "", this.northWest[b].color.styleB, "", this.north[b].color.styleB, "", this.northEast[b].color.styleB, "", this.northWest[b].color.styleB,
                //     "", this.north[b].color.styleB, "", this.northEast[b].color.styleB, "", this.northWest[b].color.styleB, "", this.north[b].color.styleB, "", this.northEast[b].color.styleB, "", this.northWest[b].color.styleB, "", this.north[b].color.styleB, "", this.northEast[b].color.styleB, "", this.west[b].color.styleB, "", this.origin[b].color.styleB, "", this.east[b].color.styleB, "", this.west[b].color.styleB, "", this.origin[b].color.styleB, "", this.east[b].color.styleB, "", this.west[b].color.styleB, "", this.origin[b].color.styleB, "",
                //     this.east[b].color.styleB, "", this.west[b].color.styleB, "", this.origin[b].color.styleB, "", this.east[b].color.styleB, "", this.west[b].color.styleB, "", this.origin[b].color.styleB, "", this.east[b].color.styleB, "", this.southWest[b].color.styleB, "", this.south[b].color.styleB, "", this.southEast[b].color.styleB, "", this.southWest[b].color.styleB, "", this.south[b].color.styleB, "", this.southEast[b].color.styleB, "", this.southWest[b].color.styleB, "", this.south[b].color.styleB, "", this.southEast[b].color.styleB, "",
                //     this.southWest[b].color.styleB, "", this.south[b].color.styleB, "", this.southEast[b].color.styleB, "", this.southWest[b].color.styleB, "", this.south[b].color.styleB, "", this.southEast[b].color.styleB, "")
            },
            map: function() {
                this.origin = this.cubelets[4];
                this.north = this.cubelets[1];
                this.northEast = this.cubelets[2];
                this.east = this.cubelets[5];
                this.southEast = this.cubelets[8];
                this.south = this.cubelets[7];
                this.southWest = this.cubelets[6];
                this.west = this.cubelets[3];
                this.northWest = this.cubelets[0];
                for (var a = 0; 6 > a; a++)
                    if (this.origin.faces[a].color &&
                        this.origin.faces[a].color !== COLORLESS) {
                        this.color = this.origin.faces[a].color;
                        this.face = Direction.getNameById(a);
                        break
                    } this.up = new Group(this.northWest, this.north, this.northEast);
                this.equator = new Group(this.west, this.origin, this.east);
                this.down = new Group(this.southWest, this.south, this.southEast);
                this.left = new Group(this.northWest, this.west, this.southWest);
                this.middle = new Group(this.north, this.origin, this.south);
                this.right = new Group(this.northEast, this.east, this.southEast);
                (a = this.hasType("center")) &&
                1 === a.cubelets.length ? (this.center = this.hasType("center"), this.corners = new Group(this.hasType("corner")), this.cross = new Group(this.center, this.hasType("edge")), this.ex = new Group(this.center, this.hasType("corner"))) : this.centers = new Group(this.hasType("center"));
                this.edges = new Group(this.hasType("edge"));
                this.ring = new Group(this.northWest, this.north, this.northEast, this.west, this.east, this.southWest, this.south, this.southEast);
                this.dexter = new Group(this.northWest, this.origin, this.southEast);
                this.sinister =
                    new Group(this.northEast, this.origin, this.southWest)
            },
            getLocation: function(a) {
                return a === this.origin ? "origin" : a === this.north ? "north" : a === this.northEast ? "northEast" : a === this.east ? "east" : a === this.southEast ? "southEast" : a === this.south ? "south" : a === this.southWest ? "southWest" : a === this.west ? "west" : a === this.northWest ? "northWest" : !1
            }
        });
        learn(Slice.prototype, Group.prototype)
    });

    function Solver() {
        this.logic = function(a) {
            return !1
        }
    }
    Solver.prototype.consider = function(a) {
        if (void 0 === a) return console.warn("A cube [Cube] argument must be specified for Solver.consider()."), !1;
        if (!1 === a instanceof Cube) return console.warn("The cube argument provided is not a valid Cube."), !1;
        a.isShuffling = !1;
        return a.isSolved() ? (.5 <= erno.verbosity && Solver.prototype.explain("I\u2019ve found that the cube is already solved."), !1) : this.logic(a)
    };
    Solver.prototype.hint = function(a) {
        // console.log("%c" + a + "%c\n", "background-color: #EEE; color: #333", "")
    };
    Solver.prototype.explain = function(a) {
        // console.log("Solver says: %c " + a + " %c\n", "color: #080", "")
    };

    function Twist(a, b) {
        var c = {
            X: "Cube on X",
            L: "Left face",
            M: "Middle slice",
            R: "Right face",
            Y: "Cube on Y",
            U: "Up face",
            E: "Equator slice",
            D: "Down face",
            Z: "Cube on Z",
            F: "Front face",
            S: "Standing slice",
            B: "Back face"
        } [a.toUpperCase()];
        if (void 0 !== c) {
            void 0 != b && 0 > b && (a = a.invert(), b = b.absolute());
            var d = 0,
                e = "unwise";
            a === a.toUpperCase() ? (d = 1, e = "clockwise") : a === a.toLowerCase() && (d = -1, e = "anticlockwise");
            this.command = a;
            this.group = c;
            this.degrees = b;
            this.vector = d;
            this.wise = e;
            this.created = Date.now();
            this.getInverse = function() {
                return new Twist(a.invert(),
                    b)
            }
        } else return !1
    }

    Twist.validate = function() {
        var a = Array.prototype.slice.call(arguments),
            b, c;
        for (b = 0; b < a.length; b++) {
            var d = a[b];
            lookAhead = b + 1 < a.length ? a[b + 1] : void 0;
            if (!(d instanceof Twist))
                if ("string" === typeof d)
                    if (1 === d.length) a[b] = "number" === typeof lookAhead ? new Twist(d, lookAhead) : new Twist(d);
                    else {
                        if (1 < d.length) {
                            var e = /(-?\d+|[XLMRYUEDZFSB])/gi;
                            d = d.match(e);
                            for (c = 0; c < d.length; c++) {
                                var f = d[c];
                                if (isNumeric(f)) d[c] = +f;
                                else {
                                    e = d.slice(0, c);
                                    var g = d.slice(c + 1);
                                    f = f.split("");
                                    d = e.concat(f, g)
                                }
                            }
                            e = a.slice(0, b);
                            g = a.slice(b +
                                1);
                            a = e.concat(d, g);
                            b--
                        }
                    }
            else d instanceof Direction ? a[b] = d.initial : d instanceof Array ? (e = a.slice(0, b), g = a.slice(b + 1), a = e.concat(d, g)) : a.splice(b, 1), b--
        }
        return a
    };
};