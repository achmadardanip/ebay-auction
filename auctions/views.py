from django.contrib.auth import authenticate, login, logout
from django.core import paginator
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, response
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import *


def index(request):
    items = Listing.objects.all().order_by('-time')
    try: 
        w = Watchlist.objects.filter(user=request.user.username)
        wcount = len(w)
    except:
        wcount = None
    
    try:
        paginator = Paginator(items, 8)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = None
    return render(request, "auctions/index.html", {
        # "items": items,
        "wcount": wcount,
        "items":page_obj
    })

def create(request):
    category = Category.objects.raw("SELECT * FROM auctions_category")
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount = len(w)
    except:
        wcount = None
    return render(request, "auctions/create.html", {
        "category": category,
        "wcount": wcount
    })

def submit(request):
    if request.method == "POST":
        listTable = Listing()
        now = datetime.now()
        dt = now.strftime(" %d %B %Y, %H:%M:%S ")
        listTable.owner = request.user.username
        listTable.title = request.POST.get('title')
        listTable.description = request.POST.get('description')
        listTable.price = request.POST.get('price')
        listTable.category = request.POST.get('category')
        listTable.condition = request.POST.get('condition')
        if request.POST.get('link'):
            listTable.link = request.POST.get('link')
        else:
            listTable.link = "http://mti.fti.upnyk.ac.id/asset/images/no-image.png"
        listTable.time = dt
        listTable.save()
        all = allListing()
        items = Listing.objects.all()
        for i in items:
            try:
                if allListing.objects.get(listingId=i.id):
                    pass
            except:
                all.listingId = i.id
                all.title = i.title
                all.description = i.description
                all.category = i.category
                all.link = i.link
                all.time = i.time
                all.save()
        return redirect('index')
    else:
        return redirect('index')

@login_required(login_url=settings.LOGIN_URL)
def listingpage(request,id):
    try:
        item = Listing.objects.get(id=id)
    except:
        return redirect('index')
    try:
        comments = Comment.objects.filter(listingId=id).order_by('-time')
    except:
        comments = None
    if request.user.username:
        try:
            if Watchlist.objects.get(user=request.user.username,listingId=id):
                added=True
        except:
            added = False
        try:
            l = Listing.objects.get(id=id)
            if l.owner == request.user.username :
                owner=True
            else:
                owner=False
        except:
            return redirect('index')
    else:
        added=False
        owner=False
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount=len(w)
    except:
        wcount=None
    try:
        bidder = Bid.objects.filter(listingId=id)
        bcount = len(bidder)
    except:
        bcount = None
    try:
        relatedprod = Listing.objects.get(id=id)
        relatedprodcat = relatedprod.category
        relatedprods = Listing.objects.filter(category=relatedprodcat).filter(~Q(id=id))[:3]
    except:
        relatedprods = None
    try:
        bidders = Bid.objects.filter(listingId=id).order_by('-time')
    except:
        bidders = None
    return render(request,"auctions/listingpage.html",{
        "i":item,
        "error":request.COOKIES.get('error'),
        "success":request.COOKIES.get('success'),
        "addwatchlist": request.COOKIES.get('addwatchlist'),
        "removewatchlist": request.COOKIES.get('removewatchlist'),
        "comments":comments,
        "bcount": bcount,
        "added":added,
        "owner":owner,
        "wcount":wcount,
        "relatedprod": relatedprods,
        "bidders": bidders
    })

def addwatchlist(request, listingid):
    if request.user.username:
        w = Watchlist()
        now = datetime.now()
        dt = now.strftime(" %d %B %Y, %H:%M:%S ")
        w.user = request.user.username
        w.listingId = listingid
        w.time = dt
        w.save()
        response = redirect('listingpage', id=listingid)
        response.set_cookie('addwatchlist', 'This list has been added successfully to your watchlist', max_age=3)
        return response
    else:
        return redirect('index')

def removewatchlist(request, listingid):
    if request.user.username:
        try:
            w = Watchlist.objects.get(user=request.user.username, listingId = listingid)
            w.delete()
            response = redirect('listingpage', id=listingid)
            response.set_cookie('removewatchlist', 'This list has been removed from your watchlist', max_age=3)
            return response
        except:
            return redirect('listingpage', id=listingid)
    else:
        return redirect('index') 

def bidsubmit(request, listingid):
    current_bid = Listing.objects.get(id=listingid)
    current_bid = current_bid.price
    if request.method == "POST":
        now = datetime.now()
        dt = now.strftime(" %d %B %Y, %H:%M:%S ")
        user_bid = float(request.POST.get('bid'))
        try:
            isBidExists = Bid.objects.filter(listingId=listingid)
            isBidExist = len(isBidExists)
        except:
            isBidExist = None
        if isBidExist == 0:
            if user_bid >= float(current_bid):
                listing_items = Listing.objects.get(id=listingid)
                listing_items.price = user_bid
                listing_items.save()
                try:
                    if Bid.objects.filter(id=listingid):
                        bidrow = Bid.objects.filter(id=listingid)
                        bidrow.delete()
                    bidtable = Bid()
                    bidtable.user = request.user.username
                    bidtable.title = listing_items.title
                    bidtable.listingId = listingid
                    bidtable.bid = user_bid
                    bidtable.time = dt
                    bidtable.save()
                except:
                    bidtable = Bid()
                    bidtable.user = request.user.username
                    bidtable.title = listing_items.title
                    bidtable.listingId = listingid
                    bidtable.bid = user_bid
                    bidtable.time = dt
                    bidtable.save()
                response = redirect('listingpage', id=listingid)
                response.set_cookie('success', 'Bid successful! Your bid is the current bid', max_age=3)
                return response
            else:
                response = redirect('listingpage', id=listingid)
                response.set_cookie('error', 'Bid should be greater than the starting bid', max_age=3)
                return response
        else:
            if user_bid > float(current_bid):
                listing_items = Listing.objects.get(id=listingid)
                listing_items.price = user_bid
                listing_items.save()
                try:
                    if Bid.objects.filter(id=listingid):
                        bidrow = Bid.objects.filter(id=listingid)
                        bidrow.delete()
                    bidtable = Bid()
                    bidtable.user = request.user.username
                    bidtable.title = listing_items.title
                    bidtable.listingId = listingid
                    bidtable.bid = user_bid
                    bidtable.time = dt
                    bidtable.save()
                except:
                    bidtable = Bid()
                    bidtable.user = request.user.username
                    bidtable.title = listing_items.title
                    bidtable.listingId = listingid
                    bidtable.bid = user_bid
                    bidtable.time = dt
                    bidtable.save()
                response = redirect('listingpage', id=listingid)
                response.set_cookie('success', 'Bid successful! Your bid is the current bid', max_age=3)
                return response
            else:
                response = redirect('listingpage', id=listingid)
                response.set_cookie('error', 'Bid should be greater than the current bid', max_age=3)
                return response
    else:
        return redirect('index')

def closebid(request, listingid):
    if request.user.username:
        now = datetime.now()
        dt = now.strftime(" %d %B %Y, %H:%M:%S ")
        try:
            listingrow = Listing.objects.get(id=listingid)
        except:
            return redirect('index')
        closebid = Closebid()
        title = listingrow.title
        closebid.owner = listingrow.owner
        closebid.listingId = listingid
        try:
            bidrow = Bid.objects.get(listingId=listingid, bid=listingrow.price)
            closebid.winner = bidrow.user
            closebid.winprice = bidrow.bid
            closebid.time = dt
            closebid.save()
            bidrow.delete()
        except:
            closebid.winner = listingrow.owner
            closebid.winprice = listingrow.price
            closebid.time = dt
            closebid.save()
        try:
            if Watchlist.objects.filter(listingId=listingid):
                watchrow = Watchlist.objects.filter(listingId=listingid)
                watchrow.delete()
            else:
                pass
        except:
            pass
        try:
            commentrow = Comment.objects.filter(listingId=listingid)
            commentrow.delete()
        except:
            pass
        try:
            brow = Bid.objects.filter(listingId=listingid)
            brow.delete()
        except:
            pass
        try:
            cblist = Closebid.objects.get(listingId=listingid)
        except:
            closebid.owner = listingrow.owner
            closebid.winner = listingrow.owner
            closebid.listingId = listingid
            closebid.winprice = listingrow.price
            closebid.time = dt
            closebid.save()
            cblist = Closebid.objects.filter(owner=request.user.username)
        listingrow.delete()
        try:
            w = Watchlist.objects.filter(user=request.user.username)
            wcount = len(w)
        except:
            wcount: None
        return render(request, "auctions/winningpage.html", {
            "cb": cblist,
            "title":title,
            "wcount": wcount
        })
    else:
        return redirect('index')

def watchlist(request, username):
    if request.user.username:
        
        try:
            w = Watchlist.objects.filter(user=username).order_by('-time')
            items = []
            for i in w:
                items.append(Listing.objects.filter(id=i.listingId))
            try:
                w = Watchlist.objects.filter(user=request.user.username)
                wcount=len(w)
            except:
                wcount=None
            try:
                paginator = Paginator(items, 12)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
            except:
                page_obj = None
            return render(request,"auctions/watchlistpage.html",{
                "items": page_obj,
                "wcount":wcount
            })
        except:
            try:
                w = Watchlist.objects.filter(user=request.user.username)
                wcount=len(w)
            except:
                wcount=None
            return render(request,"auctions/watchlistpage.html",{
                "items":None,
                "wcount":wcount
            })
    else:
        return redirect('index')
        
@login_required(login_url=settings.LOGIN_URL)
def submitcomment(request,listingid):
    if request.method == "POST":
        now = datetime.now()
        dt = now.strftime(" %d %B %Y, %H:%M:%S ")
        c = Comment()
        c.comment = request.POST.get('comment')
        c.user = request.user.username
        c.time = dt
        c.listingId = listingid
        c.save()
        return redirect('listingpage', id=listingid)
    else:
        return redirect('index')

@login_required(login_url=settings.LOGIN_URL)
def categories(request):
    items = Category.objects.raw("SELECT * FROM auctions_category GROUP BY category")
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount = len(w)
    except:
        wcount = None
    return render(request, "auctions/category.html", {
        "items": items,
        "wcount": wcount
    })

def category(request, category):
    categoryItems = Listing.objects.filter(category=category).order_by('-time')
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount = len(w)
    except:
        wcount = None
    try:
        paginator = Paginator(categoryItems, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = None
    return render(request, "auctions/categorypage.html", {
        "items": page_obj,
        "category": category,
        "wcount": wcount
    })

def myWinnings(request):
    if request.user.username:
        items = []
        try:
            wonitems = Closebid.objects.filter(winner=request.user.username).order_by('-time')
            for w in wonitems:
                items.append(allListing.objects.filter(listingId= w.listingId))
        except:
            wonitems = None
            items = None
        try:
            w = Watchlist.objects.filter(user=request.user.username)
            wcount = len(w)
        except:
            wcount = None

        try:
            paginator = Paginator(items, 12)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
        except:
            page_obj = None

        return render(request, "auctions/myWinnings.html", {
            "wcount": wcount,
            "wonitems": wonitems,
            "items": page_obj
        })
    else:
        return redirect('index')

def allwinnings(request):
    items = []
    try:
        wonitems = Closebid.objects.all().order_by('-time')
        for w in wonitems:
            items.append(allListing.objects.filter(listingId= w.listingId))
    except:
        wonitems = None
        items = None
    try:
        paginator = Paginator(items, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = None
    return render(request, "auctions/allwinnings.html", {
        "items": page_obj,
        "wonitems": wonitems
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")